from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from deployer.models import Deployment, DeploymentMethod, Environment, Repository
import api.views

@login_required
def index(request):
    deployment_methods = DeploymentMethod.objects.all()
    repositories = Repository.objects.all()
    environments = Environment.objects.all()
    deployments = Deployment.objects.all().order_by('-created_time')[:20]
    context = {
        'deployment_methods': deployment_methods,
        'repositories': repositories,
        'environments': environments,
        'deployments': deployments,
    }
    return render_to_response('index.html', context, context_instance=RequestContext(request))


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=request.POST['username'],
                                password=request.POST['password1'])
            login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = UserCreationForm()
        context = {
            'form': form
        }
        return render_to_response('register.html', context, context_instance=RequestContext(request))
    

@login_required
@require_POST
def create_deployment(request):
    response = api.views.create_deployment(request)
    return render_to_response('deployments/index.html', response, context_instance=RequestContext(request))


@login_required
@require_POST
def abort_deployment(request, deployment_id):
    response = api.views.create_deployment(request, deployment_id)
    return render_to_response('deployments/index.html', response, context_instance=RequestContext(request))


@login_required
@require_POST
def rollback_to_deployment(request, deployment_id):
    response = api.views.rollback_to_deployment(request, deployment_id)
    return render_to_response('deployments/index.html', response, context_instance=RequestContext(request))


@login_required
@require_GET
def get_deployment(request, deployment_id):
    response = api.views.get_deployment(request, deployment_id)
    return render_to_response('deployments/index.html', context, context_instance=RequestContext(request))


@login_required
def create_repository(request):
    context = {
        'name': '',
        'location': ''
    }
    if request.method == 'POST':
        context = api.views.create_repository(request)
    return render_to_response('repositories/create.html', context, context_instance=RequestContext(request))


@login_required
def create_environment(request):
    context = {
        'name': ''
    }
    if request.method == 'POST':
        context = api.views.create_environment(request)
    return render_to_response('environments/create.html', context, context_instance=RequestContext(request))


@login_required
@require_GET
def get_environment(request, deployment_id):
    response = api.views.get_environment(request, deployment_id)
    return render_to_response('deployments/index.html', context, context_instance=RequestContext(request))


@login_required
def create_deployment_method(request):
    context = {
        'method': '',
        'base_command': ''
    }
    if request.method == 'POST':
        context = api.views.create_deployment_method(request)
    return render_to_response('deployment_methods/create.html', context, context_instance=RequestContext(request))


