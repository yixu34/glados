from django.db import models
from deployer.models import EnvironmentStageDefaults, Repository

class EnvironmentStageDefaultRepository(models.Model):
    defaults = models.ForeignKey(EnvironmentStageDefaults, related_name='defaultrepository')
    repository = models.ForeignKey(Repository)

    class Meta:
        app_label = 'deployer'
