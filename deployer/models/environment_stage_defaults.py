import simplejson
from django.db import models

class EnvironmentStageDefaults(models.Model):
    deployment_args_template = models.CharField(max_length=255)
    default_deployment_args = models.CharField(max_length=255, blank=True)
    main_repository = models.ForeignKey('Repository')

    class Meta:
        app_label = 'deployer'

    def to_dict(self):
        default_deployment_args_dict = simplejson.loads(self.default_deployment_args) \
                if self.default_deployment_args else ''
        return {
            'id': self.id,
            'deployment_args_template': self.deployment_args_template,
            'default_deployment_args': default_deployment_args_dict,
            'main_repository': self.main_repository.to_dict()
        }
