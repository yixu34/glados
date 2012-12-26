from django.db import models

class Environment(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        app_label = 'deployer'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

