from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from deployer.models import Deployment, DeploymentMethod, Environment, EnvironmentStage, Repository
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

def _textbox(label, name):
    return ('textbox', label, name, None)

def _dropdown(label, name, values):
    return ('dropdown', label, name, values)

@login_required
@require_GET
def index(request):
    deployments = Deployment.objects.all().order_by('-created_time', '-id')[:20]
    environment_stages = EnvironmentStage.objects.all()
    context = {
        'create_url': 'g_create_deployment',
        'button_text': 'Create deployment!',
        'deployments': deployments,
        'environment_stages': environment_stages
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
    context, success = _get_response_context(api.views.create_deployment(request))
    return HttpResponseRedirect(reverse('g_index'))

@login_required
@require_POST
def abort_deployment(request, deployment_id):
    # TODO:  Error handling
    context, success = _get_response_context(api.views.abort_deployment(request, deployment_id))
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
@require_GET
def repository_index(request):
    fields = [
        _textbox('Name', 'name'),
        _textbox('Location', 'location')
    ]
    repositories = Repository.objects.all()
    context = {
        'repositories': repositories,
        'fields': get_existing_field_values(request, fields),
        'create_url': 'g_create_repository',
        'button_text': 'Create repository!'
    }
    return render_to_response('repositories/index.html', context, context_instance=RequestContext(request))

@login_required
@require_POST
def create_repository(request):
    context, success = _get_response_context(api.views.create_repository(request))
    return HttpResponseRedirect(reverse('g_repository_index'))

@login_required
@require_GET
def environment_index(request):
    fields = [
        _textbox('Name', 'name')
    ]
    context = {
        'environments': [(e, e.environmentstage_set.all()) for e in Environment.objects.all()],
        'fields': get_existing_field_values(request, fields),
        'create_url': 'g_create_environment',
        'button_text': 'Create environment!'
    }
    return render_to_response('environments/index.html', context, context_instance=RequestContext(request))

@login_required
@require_POST
def create_environment(request):
    context, success = _get_response_context(api.views.create_environment(request))
    return HttpResponseRedirect(reverse('g_environment_index'))

@login_required
def create_environment_stage(request, environment_id):
    deployment_methods = map(lambda d: {'value': d.method, 'label': d.method}, DeploymentMethod.objects.all())
    fields = [
        _textbox('Stage name', 'stage_name'),
        _textbox('Defaults string', 'defaults_string'),
        _dropdown('Deployment method name', 'deployment_method_name', deployment_methods)
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
            return HttpResponseRedirect(reverse('g_environment_index'))
        else:
            raise Exception(context['error'])
    return render_to_response('environments/stages/create.html', context,
            context_instance=RequestContext(request))

@login_required
@require_GET
def get_environment_stage(request, environment_id, stage_id):
    context = {
        'stage': EnvironmentStage.objects.get(pk=stage_id),
    }
    return render_to_response('environments/stages/show.html', context,
            context_instance=RequestContext(request))

@login_required
@require_GET
def deployment_method_index(request):
    fields = [
        _textbox('Name', 'method'),
        _textbox('Command', 'base_command')
    ]
    deployment_methods = DeploymentMethod.objects.all()
    context = {
        'deployment_methods': deployment_methods,
        'fields': get_existing_field_values(request, fields),
        'create_url': 'g_create_deployment_method',
        'button_text': 'Create deployment method!'
    }
    return render_to_response('deployment_methods/index.html', context,
            context_instance=RequestContext(request))

@login_required
@require_POST
def create_deployment_method(request):
    context, success = _get_response_context(api.views.create_deployment_method(request))
    return HttpResponseRedirect(reverse('g_deployment_method_index'))

