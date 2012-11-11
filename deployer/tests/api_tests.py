import simplejson
from django.core.urlresolvers import reverse
from django.test import Client
from deployer.models import Deployment, Repository
from django.contrib.auth.models import User
from base_test_case import BaseTestCase

class ApiTests(BaseTestCase):
    fixtures = ['users', 'repositories', 'environments']

    def setUp(self):
        super(ApiTests, self).setUp()
        user_id = 1
        self.client = Client()
        user = User.objects.get(pk=1)
        result = self.client.login(username=user.username, password='foo')
        environment_stage_id = 1
        comments = 'foo bar'
        self.deployments = [
            Deployment.objects.create(environment_stage_id=environment_stage_id,
                                      user_id=user_id,
                                      comments=comments)
        ]


    def _verify_field(self, data, key, to_verify_dict=None):
        self.assertTrue(key in data, 'Expected data to contain key %s' % key)
        if to_verify_dict:
            self.assertEqual(data[key], to_verify_dict[key], 
                             'Expected data[%s] to have value %s, instead got %s' % (key, str(to_verify_dict[key]), str(data[key])))


    def _verify_response(self, response, to_verify=None):
        self.assertEqual(response.status_code, 200, 'Expected an HTTP 200')
        result = simplejson.loads(response.content)
        if not result['success']:
            self.fail('Request failed with error:  %s' % result['error'])
        data = result['data']
        if to_verify:
            for key in to_verify:
                self._verify_field(data, key, to_verify)
        return data


    def test_create_repository(self):
        kwargs = {
            'name': 'repo_name', 
            'location': 'repo_location'
        }
        response = self.client.post(reverse('g_create_repository'), kwargs)
        data = self._verify_response(response, kwargs)
        self.assertTrue('id' in data, 'Expected id to be in data')


    def _verify_repository_fields(self, repository_dict):
        self._verify_field(repository_dict, 'id')
        self._verify_field(repository_dict, 'name')
        self._verify_field(repository_dict, 'location')


    def test_get_repositories(self):
        response = self.client.get(reverse('g_get_repositories'), {})
        data = self._verify_response(response)
        for repository_dict in data:
            self._verify_repository_fields(repository_dict)
            
            
    def test_get_repository(self):
        response = self.client.get(reverse('g_get_repository', kwargs={'repository_id': 1}))
        data = self._verify_response(response)
        self._verify_repository_fields(data)


    def _verify_environment_fields(self, environment_dict):
        self._verify_field(environment_dict, 'id')
        self._verify_field(environment_dict, 'name')
        

    def test_get_environments(self):
        response = self.client.get(reverse('g_get_environments'), {})
        data = self._verify_response(response)
        for environment_dict in data:
            self._verify_environment_fields(environment_dict)


    def test_get_environment(self):
        response = self.client.get(reverse('g_get_environment', kwargs={'environment_id': 1}))
        data = self._verify_response(response)
        self._verify_environment_fields(data)


    def test_create_environment(self):
        kwargs = {
            'name': 'foobar'
        }
        response = self.client.post(reverse('g_create_environment'), kwargs)
        data = self._verify_response(response, kwargs)
        self._verify_field(data, 'id')


    def _verify_environment_stage_fields(self, environment_stage_dict, output_dict=None):
        def _verify_environment_stage_defaults_fields(stage_defaults_dict):
            self._verify_field(stage_defaults_dict, 'id')
            self._verify_field(stage_defaults_dict, 'deployment_args_template')
            self._verify_field(stage_defaults_dict, 'default_deployment_args')
            self._verify_field(stage_defaults_dict, 'main_repository')
            self._verify_repository_fields(stage_defaults_dict['main_repository'])

        def _verify_deployment_method_fields(deployment_method_dict,):
            self._verify_field(deployment_method_dict, 'id')
            self._verify_field(deployment_method_dict, 'method')
            self._verify_field(deployment_method_dict, 'base_command')

        self._verify_field(environment_stage_dict, 'id')
        self._verify_field(environment_stage_dict, 'name')
        self._verify_field(environment_stage_dict, 'environment')

        if output_dict:
            self._verify_field(environment_stage_dict, 'defaults', output_dict)
            self._verify_field(environment_stage_dict, 'deployment_method', output_dict)
        else:
            _verify_environment_stage_defaults_fields(environment_stage_dict['defaults'])
            _verify_deployment_method_fields(environment_stage_dict['deployment_method'])


    def test_get_environment_stages(self):
        response = self.client.get(reverse('g_get_environment_stages', kwargs={'environment_id': 1}))
        data = self._verify_response(response)
        for environment_stage_dict in data:
            self._verify_environment_stage_fields(environment_stage_dict)


    def test_get_environment_stage(self):
        response = self.client.get(reverse('g_get_environment_stage', kwargs={'environment_id': 1, 'stage_id': 1}))
        data = self._verify_response(response)
        self._verify_environment_stage_fields(data)


    def test_create_environment_stage(self):
        defaults_dict = {
            'deployment_args_template': 'test',
            'default_deployment_args': '',
            'main_repository': 1,
            'repositories': [1, 2]
        }
        defaults_string = simplejson.dumps(defaults_dict)
        create_args = {
            'stage_name': 'test stage',
            'defaults_string': defaults_string,
            'deployment_method_name': 'fabric'
        }
        response = self.client.post(reverse('g_create_environment_stage', kwargs={'environment_id': 1}), create_args)
        data = self._verify_response(response)

        example_output = {
            'environment': '1', 
            'deployment_method': {
                'id': 1,
                'base_command': 'fab', 
                'method': 'fabric'
            }, 
            'defaults': {
                'deployment_args_template': 'test', 
                'default_deployment_args': '', 
                'id': 4, 
                'main_repository': {
                    'location': Repository.objects.get(pk=1).location,
                    'name': 'test_code.git', 
                    'id': 1
                }
            }, 
            'name': 'test stage',
            'id': 4, 
        }
        self._verify_environment_stage_fields(data, example_output)


    def _verify_deployment_fields(self, deployment_dict):
        self._verify_field(deployment_dict, 'id')
        self._verify_field(deployment_dict, 'environment_stage')
        self._verify_field(deployment_dict, 'status')
        self._verify_field(deployment_dict, 'comments')
        self._verify_field(deployment_dict, 'deployment_args_overrides')
        self._verify_field(deployment_dict, 'created_user')
        self._verify_field(deployment_dict, 'created_time')
        self._verify_field(deployment_dict, 'started_time')
        self._verify_field(deployment_dict, 'aborted_user')
        self._verify_field(deployment_dict, 'completed_time')


    def test_get_deployments(self):
        response = self.client.get(reverse('g_get_deployments'), {})
        data = self._verify_response(response)
        for deployment_dict in data:
            self._verify_deployment_fields(deployment_dict)


    def test_get_deployment(self):
        response = self.client.get(reverse('g_get_deployment', kwargs={'deployment_id': self.deployments[0].id}), {})
        data = self._verify_response(response)
        self._verify_deployment_fields(data)


    def test_create_deployment(self):
        deployment_args_overrides = {
            'assets_repo': 'assets_repo_override'
        }
        deployment_args = {
            'environment_stage_id': 1,
            'comments': 'here are some comments',
            'deployment_args_overrides': simplejson.dumps(deployment_args_overrides)
        }
        response = self.client.post(reverse('g_create_deployment'), deployment_args)
        data = self._verify_response(response)


    def test_rollback_to_deployment(self):
        self.deployments[0].status = 'c'
        self.deployments[0].save()
        rollback_args = {
            'environment_stage_id': self.deployments[0].environment_stage_id,
            'comments': 'foo comments',
            'deployment_args_overrides': ''
        }
        response = self.client.post(reverse('g_rollback_to_deployment', kwargs={'deployment_id': self.deployments[0].id}), 
                                    rollback_args)
        data = self._verify_response(response)
        self._verify_deployment_fields(data)
        self.assertEqual(data['status'], 'i', 'Expected rollback deployment to be in progress')


    def test_abort_deployment(self):
        self.deployments[0].status = 'i'
        self.deployments[0].save()
        response = self.client.post(reverse('g_abort_deployment', kwargs={'deployment_id': self.deployments[0].id}), {})
        data = self._verify_response(response)
        self._verify_deployment_fields(data)
        self.assertEqual(data['status'], 'a', 'Expected aborted deployment to be aborted')
        
