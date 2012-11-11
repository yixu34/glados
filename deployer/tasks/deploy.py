from django.conf import settings
from celery import task

@task
def add(x, y):
    return x + y


@task
def deploy(deployment_id):
    from deployer.models import Deployment
    deployment = Deployment.objects.get(pk=deployment_id)
    Deployment.default_strategy(deployment)
    return deployment_id

