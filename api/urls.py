from django.conf.urls import patterns, url

urlpatterns = patterns('api.views',
    url(r'^deployment_methods/$', 'get_deployment_methods', name='api_get_deployment_methods'),
    url(r'^deployment_methods/create/$', 'create_deployment_method', name='api_create_deployment_method'),

    # Deployments
    url(r'^deployments/$', 'get_deployments', name='api_get_deployments'),
    url(r'^deployments/create/$', 'create_deployment', name='api_create_deployment'),
    url(r'^deployments/(?P<deployment_id>\d+)/$', 'get_deployment', name='api_get_deployment'),
    url(r'^deployments/(?P<deployment_id>\d+)/abort/$', 'abort_deployment', name='api_abort_deployment'),

    # Environments
    url(r'^environments/$', 'get_environments', name='api_get_environments'),
    url(r'^environments/create/$', 'create_environment', name='api_create_environment'),
    url(r'^environments/(?P<environment_id>\d+)/$', 'get_environment', name='api_get_environment'),

    # Environment stages
    url(r'^environments/(?P<environment_id>\d+)/stages/$',
        'get_environment_stages', name='api_get_environment_stages'),
    url(r'^environments/(?P<environment_id>\d+)/stages/create/$',
        'create_environment_stage', name='api_create_environment_stage'),
    url(r'^environments/(?P<environment_id>\d+)/stages/(?P<stage_id>\d+)/$',
        'get_environment_stage', name='api_get_environment_stage'),

    # Repositories
    url(r'^repositories/$', 'get_repositories', name='api_get_repositories'),
    url(r'^repositories/create/$', 'create_repository', name='api_create_repository'),
    url(r'^repositories/(?P<repository_id>\d+)/$', 'get_repository', name='api_get_repository'),
)
