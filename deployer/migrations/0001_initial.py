# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Repository'
        db.create_table('deployer_repository', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('location', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('deployer', ['Repository'])

        # Adding model 'Environment'
        db.create_table('deployer_environment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('deployer', ['Environment'])

        # Adding model 'DeploymentMethod'
        db.create_table('deployer_deploymentmethod', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('method', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('base_command', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('deployer', ['DeploymentMethod'])

        # Adding model 'EnvironmentStageDefaults'
        db.create_table('deployer_environmentstagedefaults', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('deployment_args_template', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('default_deployment_args', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('main_repository', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['deployer.Repository'])),
        ))
        db.send_create_signal('deployer', ['EnvironmentStageDefaults'])

        # Adding model 'EnvironmentStage'
        db.create_table('deployer_environmentstage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('defaults', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['deployer.EnvironmentStageDefaults'])),
            ('environment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['deployer.Environment'])),
            ('deployment_method', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['deployer.DeploymentMethod'])),
        ))
        db.send_create_signal('deployer', ['EnvironmentStage'])

        # Adding model 'EnvironmentStageDefaultRepository'
        db.create_table('deployer_environmentstagedefaultrepository', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('defaults', self.gf('django.db.models.fields.related.ForeignKey')(related_name='defaultrepository', to=orm['deployer.EnvironmentStageDefaults'])),
            ('repository', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['deployer.Repository'])),
        ))
        db.send_create_signal('deployer', ['EnvironmentStageDefaultRepository'])

        # Adding model 'Deployment'
        db.create_table('deployer_deployment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('environment_stage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['deployer.EnvironmentStage'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('comments', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('deployment_args_overrides', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('created_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='createddeployment_set', to=orm['auth.User'])),
            ('aborted_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aborteddeployment_set', null=True, to=orm['auth.User'])),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('started_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('completed_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('task_id', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('deployer', ['Deployment'])


    def backwards(self, orm):
        # Deleting model 'Repository'
        db.delete_table('deployer_repository')

        # Deleting model 'Environment'
        db.delete_table('deployer_environment')

        # Deleting model 'DeploymentMethod'
        db.delete_table('deployer_deploymentmethod')

        # Deleting model 'EnvironmentStageDefaults'
        db.delete_table('deployer_environmentstagedefaults')

        # Deleting model 'EnvironmentStage'
        db.delete_table('deployer_environmentstage')

        # Deleting model 'EnvironmentStageDefaultRepository'
        db.delete_table('deployer_environmentstagedefaultrepository')

        # Deleting model 'Deployment'
        db.delete_table('deployer_deployment')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'deployer.deployment': {
            'Meta': {'object_name': 'Deployment'},
            'aborted_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aborteddeployment_set'", 'null': 'True', 'to': "orm['auth.User']"}),
            'comments': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'completed_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'createddeployment_set'", 'to': "orm['auth.User']"}),
            'deployment_args_overrides': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'environment_stage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['deployer.EnvironmentStage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'started_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'deployer.deploymentmethod': {
            'Meta': {'object_name': 'DeploymentMethod'},
            'base_command': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'deployer.environment': {
            'Meta': {'object_name': 'Environment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'deployer.environmentstage': {
            'Meta': {'object_name': 'EnvironmentStage'},
            'defaults': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['deployer.EnvironmentStageDefaults']"}),
            'deployment_method': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['deployer.DeploymentMethod']"}),
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['deployer.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'deployer.environmentstagedefaultrepository': {
            'Meta': {'object_name': 'EnvironmentStageDefaultRepository'},
            'defaults': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'defaultrepository'", 'to': "orm['deployer.EnvironmentStageDefaults']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['deployer.Repository']"})
        },
        'deployer.environmentstagedefaults': {
            'Meta': {'object_name': 'EnvironmentStageDefaults'},
            'default_deployment_args': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'deployment_args_template': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_repository': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['deployer.Repository']"})
        },
        'deployer.repository': {
            'Meta': {'object_name': 'Repository'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['deployer']