import os
import signal
from celery import task
from celery.worker import state
import celery.worker.job
from celery.signals import task_revoked
from celery.task.control import inspect
from django.core.exceptions import ObjectDoesNotExist

@task
def add(x, y):
    return x + y

@task
def deploy(deployment_id):
    from deployer.models import Deployment
    deployment = Deployment.objects.get(pk=deployment_id)
    deployment.task_id = deploy.request.id
    deployment.save()
    Deployment.default_strategy(deployment)
    return deployment_id

@task_revoked.connect
def on_deploy_revoked(*args, **kwargs):
    from deployer.models import Deployment
    deployments = Deployment.objects.filter(subprocess_pid__isnull=False)
    for deployment in deployments:
        try:
            os.kill(deployment.subprocess_pid, signal.SIGTERM)
        finally:
            # If something went wrong, then presumably the process doesn't exist anymore.
            deployment.subprocess_pid = None
            deployment.save()

