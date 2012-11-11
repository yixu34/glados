from django.db import models
from django.conf import settings
import os
import subprocess

class Repository(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, unique=True)

    class Meta:
        app_label = 'deployer'

    def bootstrap_checkout(self):
        remote_repository_path = self.location
        local_repository_path = os.path.join(settings.DEPLOYMENT_PATH, self.name)

        if not os.path.exists(settings.DEPLOYMENT_PATH):
            os.makedirs(settings.DEPLOYMENT_PATH)

        if not os.path.exists(local_repository_path):
            # TODO:  Generalize this to other VCS systems?
            s = 'git clone %s %s' % (self.location, self.name)

            subprocess.check_call('git clone %s %s' % (self.location, self.name),
                                  shell=True,
                                  cwd=settings.DEPLOYMENT_PATH)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location
        }
 
