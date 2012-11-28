from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from api import urls
import views
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='g_index'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^register/$', 'views.register', name='g_register'),

    # Deployments
    url(r'^deployments/create/$', 'views.create_deployment', name='g_create_deployment'),
    url(r'^deployments/(?P<deployment_id>\d+)/abort/$', 'views.abort_deployment', name='g_abort_deployment'),
    url(r'^deployments/(?P<deployment_id>\d+)/rollback/$', 'views.rollback_to_deployment', name='g_rollback_to_deployment'),
    url(r'^deployments/(?P<deployment_id>\d+)/$', 'views.get_deployment', name='g_get_deployment'),

    # Deployment methods
    url(r'^deployment_methods/create/$', 'views.create_deployment_method', name='g_create_deployment_method'),

    # Repositories
    url(r'^repositories/create/$', 'views.create_repository', name='g_create_repository'),

    # Environments
    url(r'^environments/create/$', 'views.create_environment', name='g_create_environment'),
    url(r'^environments/(?P<environment_id>\d+)/$', 'views.get_environment', name='g_get_environment'),

    # Environment stages

    url(r'^api/', include('api.urls')),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
)
