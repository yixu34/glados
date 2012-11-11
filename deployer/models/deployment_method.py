from django.db import models

class DeploymentMethod(models.Model):
    method = models.CharField(max_length=64, unique=True)
    base_command = models.CharField(max_length=255)

    class Meta:
        app_label = 'deployer'

    def to_dict(self):
        return {
            'id': self.id,
            'method': self.method,
            'base_command': self.base_command
        }
