from django.conf import settings
from celery import task
import logging

logger = logging.getLogger(settings.APP_LOG)

@task
def add(x, y):
    return x + y


@task
def deploy(deployment_id):
    from deployer.models import Deployment
    deployment = Deployment.objects.get(pk=deployment_id)
    deployment.task_id = deploy.request.id
    deployment.save()
    logger.debug('inside deploy task')
    Deployment.default_strategy(deployment)
    return deployment_id

