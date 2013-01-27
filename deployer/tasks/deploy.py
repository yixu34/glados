import os
import signal
from celery import task
from celery.worker import state
import celery.worker.job
from celery.signals import task_revoked, worker_shutdown
from celery.task.control import inspect
from django.conf import settings
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
    pid_paths = [os.path.join(settings.PID_FILE_ROOT, f) for f in os.listdir(settings.PID_FILE_ROOT)]
    filenames_and_pids = dict((filename, None) for filename in pid_paths)
    for pid_filename in filenames_and_pids:
        with open(pid_filename, 'r') as pid_file:
            filenames_and_pids[pid_filename] = int(pid_file.readline().strip())
    for pid_filename, pid in filenames_and_pids.iteritems():
        try:
            os.kill(pid, signal.SIGKILL)
            os.remove(pid_filename)
        except OSError:
            pass


from celery import platforms
from celery.signals import worker_process_init

def cleanup_after_tasks(signum, frame):
    print 'deploy revoked'
    on_deploy_revoked()

def install_pool_process_sighandlers(**kwargs):
    platforms.signals['TERM'] = cleanup_after_tasks
    platforms.signals['INT'] = cleanup_after_tasks

#import celery.apps.worker
#celery.apps.worker.install_worker_term_handler(on_deploy_revoked)

#worker_process_init.connect(install_pool_process_sighandlers)
