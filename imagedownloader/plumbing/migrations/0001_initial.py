# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Process'
        db.create_table('plumbing_process', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('progress', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('executing', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('plumbing', ['Process'])

        # Adding model 'ComplexProcess'
        db.create_table('plumbing_complexprocess', (
            ('process_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['plumbing.Process'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('plumbing', ['ComplexProcess'])

        # Adding model 'ProcessOrder'
        db.create_table('plumbing_processorder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('process', self.gf('django.db.models.fields.related.ForeignKey')(related_name='used_by', to=orm['plumbing.Process'])),
            ('complex_process', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['plumbing.ComplexProcess'])),
        ))
        db.send_create_signal('plumbing', ['ProcessOrder'])

        # Adding model 'Program'
        db.create_table('plumbing_program', (
            ('complexprocess_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['plumbing.ComplexProcess'], unique=True, primary_key=True)),
            ('automatic_download', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requester.AutomaticDownload'])),
        ))
        db.send_create_signal('plumbing', ['Program'])

        # Adding model 'FilterSolarElevation'
        db.create_table('plumbing_filtersolarelevation', (
            ('process_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['plumbing.Process'], unique=True, primary_key=True)),
            ('minimum', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
        ))
        db.send_create_signal('plumbing', ['FilterSolarElevation'])

        # Adding model 'CollectTimed'
        db.create_table('plumbing_collecttimed', (
            ('process_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['plumbing.Process'], unique=True, primary_key=True)),
            ('monthly', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('plumbing', ['CollectTimed'])

        # Adding model 'CollectChannel'
        db.create_table('plumbing_collectchannel', (
            ('process_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['plumbing.Process'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('plumbing', ['CollectChannel'])

        # Adding model 'FilterChannel'
        db.create_table('plumbing_filterchannel', (
            ('process_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['plumbing.Process'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('plumbing', ['FilterChannel'])

        # Adding M2M table for field channels on 'FilterChannel'
        db.create_table('plumbing_filterchannel_channels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('filterchannel', models.ForeignKey(orm['plumbing.filterchannel'], null=False)),
            ('channel', models.ForeignKey(orm['requester.channel'], null=False))
        ))
        db.create_unique('plumbing_filterchannel_channels', ['filterchannel_id', 'channel_id'])

        # Adding model 'FilterTimed'
        db.create_table('plumbing_filtertimed', (
            ('process_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['plumbing.Process'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('plumbing', ['FilterTimed'])

        # Adding M2M table for field time_range on 'FilterTimed'
        db.create_table('plumbing_filtertimed_time_range', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('filtertimed', models.ForeignKey(orm['plumbing.filtertimed'], null=False)),
            ('utctimerange', models.ForeignKey(orm['requester.utctimerange'], null=False))
        ))
        db.create_unique('plumbing_filtertimed_time_range', ['filtertimed_id', 'utctimerange_id'])

        # Adding model 'Compact'
        db.create_table('plumbing_compact', (
            ('process_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['plumbing.Process'], unique=True, primary_key=True)),
            ('extension', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('plumbing', ['Compact'])


    def backwards(self, orm):
        # Deleting model 'Process'
        db.delete_table('plumbing_process')

        # Deleting model 'ComplexProcess'
        db.delete_table('plumbing_complexprocess')

        # Deleting model 'ProcessOrder'
        db.delete_table('plumbing_processorder')

        # Deleting model 'Program'
        db.delete_table('plumbing_program')

        # Deleting model 'FilterSolarElevation'
        db.delete_table('plumbing_filtersolarelevation')

        # Deleting model 'CollectTimed'
        db.delete_table('plumbing_collecttimed')

        # Deleting model 'CollectChannel'
        db.delete_table('plumbing_collectchannel')

        # Deleting model 'FilterChannel'
        db.delete_table('plumbing_filterchannel')

        # Removing M2M table for field channels on 'FilterChannel'
        db.delete_table('plumbing_filterchannel_channels')

        # Deleting model 'FilterTimed'
        db.delete_table('plumbing_filtertimed')

        # Removing M2M table for field time_range on 'FilterTimed'
        db.delete_table('plumbing_filtertimed_time_range')

        # Deleting model 'Compact'
        db.delete_table('plumbing_compact')


    models = {
        'plumbing.collectchannel': {
            'Meta': {'object_name': 'CollectChannel', '_ormbases': ['plumbing.Process']},
            'process_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['plumbing.Process']", 'unique': 'True', 'primary_key': 'True'})
        },
        'plumbing.collecttimed': {
            'Meta': {'object_name': 'CollectTimed', '_ormbases': ['plumbing.Process']},
            'monthly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'process_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['plumbing.Process']", 'unique': 'True', 'primary_key': 'True'})
        },
        'plumbing.compact': {
            'Meta': {'object_name': 'Compact', '_ormbases': ['plumbing.Process']},
            'extension': ('django.db.models.fields.TextField', [], {}),
            'process_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['plumbing.Process']", 'unique': 'True', 'primary_key': 'True'})
        },
        'plumbing.complexprocess': {
            'Meta': {'object_name': 'ComplexProcess', '_ormbases': ['plumbing.Process']},
            'process_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['plumbing.Process']", 'unique': 'True', 'primary_key': 'True'}),
            'processes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'complex_process'", 'symmetrical': 'False', 'through': "orm['plumbing.ProcessOrder']", 'to': "orm['plumbing.Process']"})
        },
        'plumbing.filterchannel': {
            'Meta': {'object_name': 'FilterChannel', '_ormbases': ['plumbing.Process']},
            'channels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['requester.Channel']", 'db_index': 'True', 'symmetrical': 'False'}),
            'process_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['plumbing.Process']", 'unique': 'True', 'primary_key': 'True'})
        },
        'plumbing.filtersolarelevation': {
            'Meta': {'object_name': 'FilterSolarElevation', '_ormbases': ['plumbing.Process']},
            'minimum': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'process_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['plumbing.Process']", 'unique': 'True', 'primary_key': 'True'})
        },
        'plumbing.filtertimed': {
            'Meta': {'object_name': 'FilterTimed', '_ormbases': ['plumbing.Process']},
            'process_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['plumbing.Process']", 'unique': 'True', 'primary_key': 'True'}),
            'time_range': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['requester.UTCTimeRange']", 'db_index': 'True', 'symmetrical': 'False'})
        },
        'plumbing.process': {
            'Meta': {'object_name': 'Process'},
            'description': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'executing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'progress': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'})
        },
        'plumbing.processorder': {
            'Meta': {'object_name': 'ProcessOrder'},
            'complex_process': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['plumbing.ComplexProcess']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'process': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'used_by'", 'to': "orm['plumbing.Process']"})
        },
        'plumbing.program': {
            'Meta': {'object_name': 'Program', '_ormbases': ['plumbing.ComplexProcess']},
            'automatic_download': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requester.AutomaticDownload']"}),
            'complexprocess_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['plumbing.ComplexProcess']", 'unique': 'True', 'primary_key': 'True'})
        },
        'requester.account': {
            'Meta': {'object_name': 'Account'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.TextField', [], {})
        },
        'requester.area': {
            'Meta': {'object_name': 'Area'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'east_longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'hourly_longitude': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '5', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'north_latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'south_latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'west_longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'})
        },
        'requester.automaticdownload': {
            'Meta': {'object_name': 'AutomaticDownload'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requester.Area']"}),
            'channels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['requester.Channel']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requester.EmailAccount']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_simultaneous_request': ('django.db.models.fields.IntegerField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'paused': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'root_path': ('django.db.models.fields.TextField', [], {}),
            'time_range': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requester.UTCTimeRange']"}),
            'title': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        'requester.channel': {
            'Meta': {'object_name': 'Channel'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_file': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_index': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'satellite': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requester.Satellite']"})
        },
        'requester.emailaccount': {
            'Meta': {'object_name': 'EmailAccount', '_ormbases': ['requester.Account']},
            'account_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['requester.Account']", 'unique': 'True', 'primary_key': 'True'}),
            'hostname': ('django.db.models.fields.TextField', [], {}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'username': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        },
        'requester.satellite': {
            'Meta': {'object_name': 'Satellite'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identification': ('django.db.models.fields.TextField', [], {}),
            'in_file': ('django.db.models.fields.TextField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'request_server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requester.WebServerAccount']"})
        },
        'requester.serveraccount': {
            'Meta': {'object_name': 'ServerAccount', '_ormbases': ['requester.Account']},
            'account_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['requester.Account']", 'unique': 'True', 'primary_key': 'True'}),
            'username': ('django.db.models.fields.TextField', [], {})
        },
        'requester.utctimerange': {
            'Meta': {'object_name': 'UTCTimeRange'},
            'begin': ('django.db.models.fields.DateTimeField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'requester.webserveraccount': {
            'Meta': {'object_name': 'WebServerAccount', '_ormbases': ['requester.ServerAccount']},
            'serveraccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['requester.ServerAccount']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['plumbing']