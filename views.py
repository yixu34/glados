from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from deployer.models import Deployment, DeploymentMethod, Environment, Repository
from util.helpers import get_existing_field_values
import simplejson
import api.views

def _get_response_context(response):
    content = simplejson.loads(response.content)
    success = content['success']
    return content, success

def _merge_contexts(*contexts):
    result = {}
    for context in contexts:
        result.update(context)
    return result

def _get_and_merge_contexts(response, *existing_contexts):
    context, success = _get_response_context(response)
    merged =_merge_contexts(context, *existing_contexts)
    return merged, success

@login_required
def index(request):
    deployment_methods = DeploymentMethod.objects.all()
    repositories = Repository.objects.all()
    environments = Environment.objects.all()
    deployments = Deployment.objects.all().order_by('-created_time', '-id')[:20]
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
def create_deployment(request):
    fields = [
        ('Environment stage id', 'environment_stage_id'),
        ('Comments', 'comments'),
        ('Argument overrides', 'deployment_args_overrides')
    ]
    context = {
        'fields': get_existing_field_values(request, fields),
        'create_url': 'g_create_deployment',
        'button_text': 'Create deployment!'
    }
    if request.method == 'POST':
        context, success = _get_and_merge_contexts(api.views.create_deployment(request), context)
        if success:
            return HttpResponseRedirect(reverse('g_index'))
    return render_to_response('create.html', context, context_instance=RequestContext(request))

@login_required
@require_POST
def abort_deployment(request, deployment_id):
    # TODO:  Error handling
    context, success = _get_response_context(api.views.create_deployment(request, deployment_id))
    return HttpResponseRedirect(reverse('g_get_deployment', kwargs={'deployment_id': deployment_id}))

@login_required
@require_POST
def rollback_to_deployment(request, deployment_id):
    # TODO:  Error handling
    context, success = _get_response_context(api.views.rollback_to_deployment(request, deployment_id))
    if success:
        return HttpResponseRedirect(reverse('g_index'))
    return render_to_response('deployments/index.html', context, context_instance=RequestContext(request))

@login_required
@require_GET
def get_deployment(request, deployment_id):
    # TODO:  Error handling
    context, success = _get_response_context(api.views.get_deployment(request, deployment_id))
    return render_to_response('deployments/index.html', context, context_instance=RequestContext(request))

@login_required
def create_repository(request):
    fields = [
        ('Name', 'name'),
        ('Location', 'location')
    ]
    context = {
        'fields': get_existing_field_values(request, fields),
        'create_url': 'g_create_repository',
        'button_text': 'Create repository!'
    }
    if request.method == 'POST':
        context, success = _get_and_merge_contexts(api.views.create_repository(request), context)
        if success:
            return HttpResponseRedirect(reverse('g_index'))
    return render_to_response('create.html', context, context_instance=RequestContext(request))

@login_required
def create_environment(request):
    fields = [
        ('Name', 'name')
    ]
    context = {
        'fields': get_existing_field_values(request, fields),
        'create_url': 'g_create_environment',
        'button_text': 'Create environment!'
    }
    if request.method == 'POST':
        context, success = _get_and_merge_contexts(api.views.create_environment(request), context)
        if success:
            return HttpResponseRedirect(reverse('g_index'))
    return render_to_response('create.html', context, context_instance=RequestContext(request))

@login_required
def create_environment_stage(request, environment_id):
    fields = [
        ('Stage name', 'stage_name'),
        ('Defaults string', 'defaults_string'),
        ('Deployment method name', 'deployment_method_name')
    ]
    context = {
        'fields': get_existing_field_values(request, fields),
        'create_url': 'g_create_environment_stage',
        'button_text': 'Create environment stage!',
        'url_args': environment_id
    }
    if request.method == 'POST':
        context, success = _get_and_merge_contexts(
                api.views.create_environment_stage(request, environment_id), context)
        if success:
            return HttpResponseRedirect(reverse('g_index'))
    return render_to_response('create.html', context, context_instance=RequestContext(request))

@login_required
@require_GET
def get_environment(request, environment_id):
    def _response(context):
        return render_to_response('environments/index.html', context,
               context_instance=RequestContext(request))

    environment, environment_success = _get_response_context(
            api.views.get_environment(request, environment_id))
    if not environment_success:
        return _response(environment)

    stages, stages_success = _get_response_context(
            api.views.get_environment_stages(request, environment_id))
    if not stages_success:
        return _response(stages)

    if 'data' in stages:
        environment['data']['stages'] = stages['data']
    return _response(environment)

@login_required
def create_deployment_method(request):
    fields = [
        ('Method name', 'method'),
        ('Command', 'base_command')
    ]
    context = {
        'fields': get_existing_field_values(request, fields),
        'create_url': 'g_create_deployment_method',
        'button_text': 'Create deployment method!'
    }
    if request.method == 'POST':
        context, success = _get_and_merge_contexts(api.views.create_deployment_method(request), context)
        if success:
            return HttpResponseRedirect(reverse('g_index'))
    return render_to_response('create.html', context, context_instance=RequestContext(request))

