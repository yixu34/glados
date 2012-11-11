import re
import simplejson
from django.db import models
from deployer.models import Environment, DeploymentMethod, EnvironmentStageDefaults

class EnvironmentStage(models.Model):
    name = models.CharField(max_length=64)
    defaults = models.ForeignKey(EnvironmentStageDefaults)
    environment = models.ForeignKey(Environment)
    deployment_method = models.ForeignKey(DeploymentMethod)

    unique_together = ('name', 'environment')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'defaults': self.defaults.to_dict(), 
            'environment': self.environment_id,
            'deployment_method': self.deployment_method.to_dict()
        }

    class Meta:
        app_label = 'deployer'

    def bootstrap_checkout_repositories(self):
        for stage_default_repository in self.defaults.defaultrepository.all():
            stage_default_repository.repository.bootstrap_checkout()

    def get_deployment_args_dict(self, deployment_args_overrides):
        args_dict = simplejson.loads(self.defaults.default_deployment_args) if self.defaults.default_deployment_args else {}
        if deployment_args_overrides:
            overrides_dict = simplejson.loads(deployment_args_overrides)
            args_dict.update(overrides_dict)
        return args_dict
        
    def expand_deployment_args(self, deployment_args_overrides):
        expanded_args = self.defaults.deployment_args_template
        args_dict = self.get_deployment_args_dict(deployment_args_overrides)
        for arg_name, arg_value in args_dict.iteritems():
            variable_pattern = '\$\(%s\)' % arg_name
            expanded_args = re.sub(variable_pattern, arg_value, expanded_args)
        return expanded_args

