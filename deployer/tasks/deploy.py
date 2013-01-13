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
    print 'Deployments = %s' % str([d.id for d in deployments])
    for deployment in deployments:
        print 'Killing %i' % deployment.subprocess_pid
        os.kill(deployment.subprocess_pid, signal.SIGTERM)
        deployment.subprocess_pid = None
        deployment.save()

