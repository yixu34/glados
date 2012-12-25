from datetime import datetime
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from deployer.models import Deployment, deployment_started, deployment_completed, deploy_strategy, Repository
from django.contrib.auth.models import User
from contextlib import contextmanager
from base_test_case import BaseTestCase
import os
import subprocess

def _empty_strategy(deployment):
    now = timezone.now()
    deployment.complete(now)

def _abort_strategy(deployment):
    now = timezone.now()
    deployment.abort(now, deployment.created_user)

def _fail_strategy(deployment):
    now = timezone.now()
    deployment.fail(now)

@contextmanager
def _override_deployment_strategy(strategy):
    old_strategy = strategy
    Deployment.default_strategy = strategy
    try:
        yield
    finally:
        Deployment.default_strategy = old_strategy


class DeploymentTests(BaseTestCase):
    fixtures = ['users', 'repositories', 'environments']

    @classmethod
    def setUpClass(cls):
        Deployment.default_strategy = _empty_strategy

    def setUp(self):
        super(DeploymentTests, self).setUp()
        self.now = datetime(2012, 11, 4, 18, 33, 3, 419330, tzinfo=timezone.utc)
        self.deployment_args = {
            'environment_stage_id': 1,
            'user_id': 1
        }

    def test_create_deployment(self):
        deployment1 = Deployment.objects.create(comments='first', **self.deployment_args)
        self.assertEqual(deployment1.status, 'r', 'Expected first deployment to be ready')
        deployment2 = Deployment.objects.create(comments='second', **self.deployment_args)
        self.assertEqual(deployment2.status, 'w', 'Expected second deployment to be waiting')
        deployment3 = Deployment.objects.create(comments='third', **self.deployment_args)
        self.assertEqual(deployment3.status, 'w', 'Expected third deployment to be waiting as well')


    def _test_update_deployment_helper(self, complete_status, strategy):
        deployment1 = Deployment.objects.create(comments='first', **self.deployment_args)
        deployment2 = Deployment.objects.create(comments='second', **self.deployment_args)
        self.assertEqual(deployment2.status, 'w', 'Expected second deployment to be waiting')

        received_signals = set()

        @receiver(deployment_started)
        def _verify_deployment_started(sender, **kwargs):
            if sender.comments == 'second':
                received_signals.add('started')

        @receiver(deployment_completed)
        def _verify_deployment_completed(sender, **kwargs):
            if sender.comments == 'first':
                received_signals.add('completed')


        with _override_deployment_strategy(strategy):
            deployment1.start(self.now)
        deployment1 = Deployment.objects.get(pk=deployment1.id)
        self.assertEqual(deployment1.status, complete_status,
                         'Expected first deployment to be marked as "%s"' % complete_status)

        self.assertTrue('completed' in received_signals,
                        'Expected to have received a signal that the first deployment completed')
        self.assertTrue('started' in received_signals,
                        'Expected to have received a signal that the second deployment started')


    def test_abort_deployment(self):
        self._test_update_deployment_helper('a', _abort_strategy)


    def test_complete_deployment(self):
        self._test_update_deployment_helper('c', _empty_strategy)


    def test_fail_deployment(self):
        self._test_update_deployment_helper('f', _fail_strategy)


    def _test_deployment_helper(self, environment_stage_id, expected_status):
        self.deployment_args['environment_stage_id'] = environment_stage_id
        deployment = Deployment.objects.create(comments='first', **self.deployment_args)
        deployment.status = 'i'
        deployment.save()
        deploy_strategy(deployment)
        self.assertEqual(deployment.status,
            expected_status,
            'Expected deployment to have status "%s", has value "%s"' % (expected_status, deployment.status))


    def test_deployment(self):
        self._test_deployment_helper(1, 'c')


    def test_deployment_error(self):
        self._test_deployment_helper(2, 'f')


    def test_deployment_with_variables(self):
        self._test_deployment_helper(3, 'c')


    def test_rollback(self):
        deployment1 = Deployment.objects.create(comments='first', **self.deployment_args)
        user = User.objects.get(pk=self.deployment_args['user_id'])
        rollback_deployment = deployment1.create_rollback(self.now, user, 'first_rollback')
        self.assertIsNone(rollback_deployment,
            'Expected rollback deployment to not be created since the first one did not succeed')

        deployment1.status = 'c'
        deployment1.save()
        deployment2 = Deployment.objects.create(comments='second', **self.deployment_args)
        deployment2.status = 'i'
        deployment2.save()
        rollback_deployment = deployment1.create_rollback(self.now, user, 'first_rollback')
        self.assertEqual(rollback_deployment.status, 'w', 'Expected rollback deployment to be waiting')

        deployment2.status = 'f'
        deployment2.save()
        rollback_deployment.status = 'f'
        rollback_deployment.save()

        rollback_deployment = deployment1.create_rollback(self.now, user, 'first_rollback')
        self.assertEqual(rollback_deployment.status, 'r', 'Expected rollback deployment to be ready')
        with _override_deployment_strategy(_empty_strategy):
            rollback_deployment.start(self.now)
        rollback_deployment = Deployment.objects.get(pk=rollback_deployment.id)
        self.assertEqual(rollback_deployment.status, 'c', 'Expected rollback deployment to have completed')

