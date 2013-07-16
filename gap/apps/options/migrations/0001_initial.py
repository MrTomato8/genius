# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'OptionChoice'
        db.create_table('options_optionchoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.SlugField')(max_length=30)),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(related_name='choices', to=orm['catalogue.Option'])),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('options', ['OptionChoice'])

        # Adding unique constraint on 'OptionChoice', fields ['option', 'code']
        db.create_unique('options_optionchoice', ['option_id', 'code'])

        # Adding M2M table for field conflicts_with on 'OptionChoice'
        db.create_table('options_optionchoice_conflicts_with', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_optionchoice', models.ForeignKey(orm['options.optionchoice'], null=False)),
            ('to_optionchoice', models.ForeignKey(orm['options.optionchoice'], null=False))
        ))
        db.create_unique('options_optionchoice_conflicts_with', ['from_optionchoice_id', 'to_optionchoice_id'])

        # Adding model 'OptionPickerGroup'
        db.create_table('options_optionpickergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('position', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0, db_index=True)),
        ))
        db.send_create_signal('options', ['OptionPickerGroup'])

        # Adding model 'OptionPicker'
        db.create_table('options_optionpicker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pickers', to=orm['options.OptionPickerGroup'])),
            ('option', self.gf('django.db.models.fields.related.OneToOneField')(related_name='picker', unique=True, to=orm['catalogue.Option'])),
            ('position', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0, db_index=True)),
            ('widget', self.gf('django.db.models.fields.CharField')(default='thumbnail', max_length=10)),
        ))
        db.send_create_signal('options', ['OptionPicker'])

        # Adding model 'ArtworkItem'
        db.create_table('options_artworkitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('image', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('uploaded_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('options', ['ArtworkItem'])


    def backwards(self, orm):
        # Removing unique constraint on 'OptionChoice', fields ['option', 'code']
        db.delete_unique('options_optionchoice', ['option_id', 'code'])

        # Deleting model 'OptionChoice'
        db.delete_table('options_optionchoice')

        # Removing M2M table for field conflicts_with on 'OptionChoice'
        db.delete_table('options_optionchoice_conflicts_with')

        # Deleting model 'OptionPickerGroup'
        db.delete_table('options_optionpickergroup')

        # Deleting model 'OptionPicker'
        db.delete_table('options_optionpicker')

        # Deleting model 'ArtworkItem'
        db.delete_table('options_artworkitem')


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
        'catalogue.option': {
            'Meta': {'object_name': 'Option'},
            'code': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Required'", 'max_length': '128'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'options.artworkitem': {
            'Meta': {'object_name': 'ArtworkItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'uploaded_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'options.optionchoice': {
            'Meta': {'ordering': "['option']", 'unique_together': "(('option', 'code'),)", 'object_name': 'OptionChoice'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '30'}),
            'conflicts_with': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'conflicts_with_rel_+'", 'blank': 'True', 'to': "orm['options.OptionChoice']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'choices'", 'to': "orm['catalogue.Option']"}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'})
        },
        'options.optionpicker': {
            'Meta': {'ordering': "['group', 'position']", 'object_name': 'OptionPicker'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pickers'", 'to': "orm['options.OptionPickerGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'picker'", 'unique': 'True', 'to': "orm['catalogue.Option']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'widget': ('django.db.models.fields.CharField', [], {'default': "'thumbnail'", 'max_length': '10'})
        },
        'options.optionpickergroup': {
            'Meta': {'ordering': "['position', 'name']", 'object_name': 'OptionPickerGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'db_index': 'True'})
        }
    }

    complete_apps = ['options']