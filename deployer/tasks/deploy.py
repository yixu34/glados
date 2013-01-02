from celery import task
from celery.signals import task_revoked

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
    # TODO:  Figure out how to get the task_id in here.
    pass
