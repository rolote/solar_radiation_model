# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'File.failures'
        db.add_column('requester_file', 'failures',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'File.failures'
        db.delete_column('requester_file', 'failures')


    models = {
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
        'requester.file': {
            'Meta': {'object_name': 'File'},
            'begin_download': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'downloaded': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'end_download': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'failures': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localname': ('django.db.models.fields.TextField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requester.Order']", 'null': 'True'}),
            'remotename': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'requester.ftpserveraccount': {
            'Meta': {'object_name': 'FTPServerAccount', '_ormbases': ['requester.ServerAccount']},
            'hostname': ('django.db.models.fields.TextField', [], {}),
            'serveraccount_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['requester.ServerAccount']", 'unique': 'True', 'primary_key': 'True'})
        },
        'requester.goesrequest': {
            'Meta': {'object_name': 'GOESRequest', '_ormbases': ['requester.Request']},
            'request_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['requester.Request']", 'unique': 'True', 'primary_key': 'True'})
        },
        'requester.order': {
            'Meta': {'object_name': 'Order'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'downloaded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'empty_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identification': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'request': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['requester.Request']", 'unique': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requester.FTPServerAccount']", 'null': 'True'})
        },
        'requester.request': {
            'Meta': {'object_name': 'Request'},
            'automatic_download': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requester.AutomaticDownload']"}),
            'begin': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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

    complete_apps = ['requester']