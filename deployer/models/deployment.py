from django.dispatch import receiver, Signal
from django.utils import timezone
from django.db import models, transaction
from deployer.models import EnvironmentStage
from django.contrib.auth.models import User
from deployer.tasks import deploy
from django.conf import settings
import subprocess
import os

deployment_started = Signal(providing_args=[])
deployment_completed = Signal(providing_args=[])


def deploy_strategy(deployment):
    try:
        stage = deployment.environment_stage
        stage.bootstrap_checkout_repositories()
        deploy_args = stage.expand_deployment_args(deployment.deployment_args_overrides)

        if not os.path.exists(settings.LOG_FILE_ROOT):
            os.makedirs(settings.LOG_FILE_ROOT)

        # Make sure the deployment command is executable from here!
        cwd = '%s%s' % (settings.DEPLOYMENT_PATH, str(stage.defaults.main_repository.name))
        log_file_path = deployment.get_log_path()
        log_file = open(log_file_path, 'w')
        subprocess.check_call('%s %s' % (stage.deployment_method.base_command, deploy_args),
                              shell=True,
                              stdout=log_file,
                              cwd=cwd)
        log_file.close()

        now = timezone.now()
        deployment.complete(now)
    except Exception as e:
        now = timezone.now()
        deployment.fail(now)


@receiver(deployment_completed)
def on_deployment_complete(sender, **kwargs):
    deployment = sender
    next_deployments = Deployment.objects.filter(environment_stage_id=deployment.environment_stage_id,
                                                 status='w').order_by('created_time')
    if next_deployments.exists():
        now = timezone.now()
        next_deployments[0].start(now)


class DeploymentManager(models.Manager):
    @transaction.commit_on_success
    def create(self, environment_stage_id, user_id, comments, deployment_args_overrides=''):
        is_blocked = self.filter(environment_stage_id=environment_stage_id,
                                 status__in=['r', 'i', 'w']).exists()
        status = 'w' if is_blocked else 'r'
        override = deployment_args_overrides or ''
        deployment = super(DeploymentManager, self).create(environment_stage_id=environment_stage_id,
                                                           created_user_id=user_id,
                                                           status=status,
                                                           comments=comments,
                                                           deployment_args_overrides=override)
        return deployment


class Deployment(models.Model):
    default_strategy = deploy_strategy

    environment_stage = models.ForeignKey(EnvironmentStage)
    STATUS_CHOICES = (
        ('r', 'Ready'),
        ('i', 'In Progress'),
        ('f', 'Failed'),
        ('c', 'Complete'),
        ('w', 'Waiting'),
        ('a', 'Aborted')
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    comments = models.CharField(max_length=255)
    deployment_args_overrides = models.CharField(max_length=255, blank=True)

    created_user = models.ForeignKey(User, related_name='createddeployment_set')

    # Can be set at most once.
    aborted_user = models.ForeignKey(User, null=True, related_name='aborteddeployment_set')
    created_time = models.DateTimeField(auto_now_add=True)
    started_time = models.DateTimeField(null=True)

    # Could be completed or aborted.
    completed_time = models.DateTimeField(null=True)

    task_id = models.CharField(max_length=255, blank=True)

    objects = DeploymentManager()

    class Meta:
        app_label = 'deployer'

    def _try_set_done_status(self, status, now, user=None):
        if self._can_be_stopped():
            self.status = status
            self.completed_time = now
            if status == 'a':
                self.aborted_user = user
            self.save()
            deployment_completed.send(sender=self)
            return True
        else:
            return False

    def start(self, now, **kwargs):
        if self.status == 'r' or self.status == 'w':
            self.status = 'i'
            self.started_time = now
            self.save()
            deployment_started.send(sender=self)
            deploy.delay(self.id)
            return True
        else:
            return False


    def _can_be_stopped(self):
        return self.status in ['i', 'w']

    def abort(self, now, user):
        return self._try_set_done_status('a', now, user)

    def complete(self, now):
        return self._try_set_done_status('c', now)

    def fail(self, now):
        return self._try_set_done_status('f', now)

    def create_rollback(self, now, user, comments, deployment_args_overrides=''):
        if self.status == 'c':
            # Only allow rollback to a successful deployment.
            return Deployment.objects.create(environment_stage_id=self.environment_stage_id,
                                             user_id=user.id,
                                             comments=comments,
                                             deployment_args_overrides=deployment_args_overrides)
        else:
            return None

    def get_log_path(self):
        return os.path.join(settings.LOG_FILE_ROOT, '%s.log' % str(self.id))

    def _get_log_contents(self):
        try:
            log_file_path = self.get_log_path()
            log_file = open(log_file_path, 'r')
            s = ''
            for line in log_file.readlines():
                s += line
            log_file.close()
            return s
        except IOError as e:
            return e.message


    def to_dict(self):
        return  {
            'id': self.id,
            'environment_stage': self.environment_stage_id,
            'status': self.status,
            'comments': self.comments,
            'deployment_args_overrides': self.deployment_args_overrides,
            'created_user': self.created_user_id,
            'created_time': str(self.created_time),
            'started_time': str(self.started_time),
            'aborted_user': self.aborted_user_id,
            'completed_time': str(self.completed_time),
            'log_contents': self._get_log_contents()
        }
