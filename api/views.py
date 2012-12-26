from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from deployer.models import Deployment, DeploymentMethod, Repository, Environment, EnvironmentStage, \
                            EnvironmentStageDefaults, EnvironmentStageDefaultRepository
from util.decorators import param_required
from util.responses import ApiSuccess, ApiError
import simplejson

@login_required
@param_required(['method', 'base_command'])
@require_POST
def create_deployment_method(request, method, base_command):
    try:
        deployment_method = DeploymentMethod.objects.create(method=method, base_command=base_command)
        return ApiSuccess(deployment_method.to_dict())
    except Exception as e:
        return ApiError(e.message)

@login_required
@require_GET
def get_deployment_methods(request):
    try:
        deployment_methods = [d.to_dict() for d in DeploymentMethod.objects.all()]
        return ApiSuccess(simplejson.dumps(deployment_methods))
    except Exception as e:
        return ApiError(e.message)

@login_required
@require_GET
def get_deployment(request, deployment_id):
    try:
        deployment = Deployment.objects.get(pk=deployment_id)
        return ApiSuccess(deployment.to_dict())
    except Exception as e:
        return ApiError(e.message)

@login_required
@require_GET
def get_deployments(request):
    try:
        deployments = [d.to_dict() for d in Deployment.objects.all()]
        return ApiSuccess(deployments)
    except Exception as e:
        return ApiError(e.message)

@login_required
@param_required(['environment_stage_id', 'comments'])
@require_POST
def create_deployment(request, environment_stage_id, comments):
    try:
        deployment_args_overrides = request.POST.get('deployment_args_overrides', '')
        deployment = Deployment.objects.create(environment_stage_id=environment_stage_id,
                                               user_id=request.user.id,
                                               comments=comments,
                                               deployment_args_overrides=deployment_args_overrides)
    except Exception as e:
        return ApiError(e.message)
    try:
        now = timezone.now()
        if deployment.status == 'r':
            deployment.start(now)
    finally:
        print 'success'
        return ApiSuccess(deployment.to_dict())

@login_required
@param_required(['comments'])
@require_POST
def rollback_to_deployment(request, deployment_id, comments):
    try:
        deployment = Deployment.objects.get(pk=deployment_id)
        now = timezone.now()
        deployment_args_overrides = request.POST.get('deployment_args_overrides', '')
        rollback_deployment = deployment.create_rollback(now, request.user, comments, deployment_args_overrides)
        if rollback_deployment and rollback_deployment.status == 'r':
            rollback_deployment.start(now)
            return ApiSuccess(rollback_deployment.to_dict())
        else:
            return ApiError('Failed to create rollback deployment')
    except Exception as e:
        return ApiError(e.message)

@login_required
@require_POST
def abort_deployment(request, deployment_id):
    try:
        deployment = Deployment.objects.get(pk=deployment_id)
        now = timezone.now()
        deployment.abort(now, request.user)
        return ApiSuccess(deployment.to_dict())
    except Exception as e:
        return ApiError(e.message)

####
@login_required
@require_GET
def get_repositories(request):
    repositories = [r.to_dict() for r in Repository.objects.all()]
    return ApiSuccess(repositories)

@login_required
@require_GET
def get_repository(request, repository_id):
    try:
        repository = Repository.objects.get(pk=repository_id)
        return ApiSuccess(repository.to_dict())
    except Exception as e:
        return ApiError(e.message)

@login_required
@param_required(['name', 'location'])
@require_POST
def create_repository(request, name, location):
    try:
        repository = Repository.objects.create(name=name, location=location)
        return ApiSuccess(repository.to_dict())
    except Exception as e:
        return ApiError(e.message)

###
@login_required
@require_GET
def get_environments(request):
    environments = [e.to_dict() for e in Environment.objects.all()]
    return ApiSuccess(environments)

@login_required
@require_GET
def get_environment(request, environment_id):
    try:
        environment = Environment.objects.get(pk=environment_id)
        return ApiSuccess(environment.to_dict())
    except Exception as e:
        return ApiError(e.message)

@login_required
@param_required('name')
@require_POST
def create_environment(request, name):
    try:
        environment = Environment.objects.create(name=name)
        return ApiSuccess(environment.to_dict())
    except Exception as e:
        return ApiError(e.message)

##
@login_required
@require_GET
def get_environment_stages(request, environment_id):
    include_parent_environment_ids = request.GET.get('include_parent_environment_ids', True)
    try:
        environment = Environment.objects.get(pk=environment_id)
        stages = [stage.to_dict(include_parent_environment_id=include_parent_environment_ids)
                  for stage in environment.environmentstage_set.all()]
        result = ApiSuccess(stages)
        return result
    except Exception as e:
        return ApiError(e.message)

@login_required
@require_GET
def get_environment_stage(request, environment_id, stage_id):
    try:
        environment = Environment.objects.get(pk=environment_id)
        stage = EnvironmentStage.objects.get(pk=stage_id)
        if stage.environment_id != environment.id:
            return ApiError('Stage id %s is not for environment %s' % (stage_id, environment_id))
        return ApiSuccess(stage.to_dict())
    except Exception as e:
        return ApiError(e.message)

@login_required
@param_required(['stage_name', 'defaults_string', 'deployment_method_name'])
@require_POST
def create_environment_stage(request, environment_id, stage_name, defaults_string, deployment_method_name):
    try:
        defaults_dict = simplejson.loads(defaults_string)
        default_deployment_args = simplejson.dumps(defaults_dict['default_deployment_args']) \
                                                       if defaults_dict['default_deployment_args'] else ''
        defaults = EnvironmentStageDefaults.objects.create(
                deployment_args_template=defaults_dict['deployment_args_template'],
                default_deployment_args=default_deployment_args,
                main_repository_id=defaults_dict['main_repository'])
        for repository_id in defaults_dict['repositories']:
            repository = Repository.objects.get(pk=repository_id)
            EnvironmentStageDefaultRepository.objects.create(defaults=defaults, repository=repository)
        deployment_method = DeploymentMethod.objects.get(method=deployment_method_name)
        stage = EnvironmentStage.objects.create(name=stage_name,
                                                defaults=defaults,
                                                environment_id=environment_id,
                                                deployment_method=deployment_method)
        return ApiSuccess(stage.to_dict())
    except Exception as e:
        return ApiError(e.message)

