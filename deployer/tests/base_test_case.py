from django.test import TestCase
from django.conf import settings
from deployer.models import Repository
import os
import subprocess

class BaseTestCase(TestCase):
    def setUp(self):
        self._override_test_repository_paths()


    def _override_test_repository_paths(self):
        for repository in Repository.objects.all():
            repository.location = os.path.join(settings.TEST_REPOSITORY_PATH, repository.name)
            repository.save()
            if not os.path.exists(repository.location):
                os.makedirs(repository.location)
                subprocess.check_call('git init --bare', cwd=repository.location, shell=True)
        for repository in Repository.objects.all():
            deployment_path = os.path.join(settings.DEPLOYMENT_PATH, repository.name)
            if not os.path.exists(deployment_path):
                os.makedirs(deployment_path)
                subprocess.check_call('cp deployer/tests/fabfile.py %s' % deployment_path, shell=True)


        
