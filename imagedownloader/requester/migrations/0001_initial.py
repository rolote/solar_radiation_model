# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Area'
        db.create_table('requester_area', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('north_latitude', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('south_latitude', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
            ('east_longitude', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('west_longitude', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('requester', ['Area'])

        # Adding model 'UTCTimeRange'
        db.create_table('requester_utctimerange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('begin', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('requester', ['UTCTimeRange'])

        # Adding model 'Account'
        db.create_table('requester_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('requester', ['Account'])

        # Adding model 'EmailAccount'
        db.create_table('requester_emailaccount', (
            ('account_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['requester.Account'], unique=True, primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.TextField')()),
            ('port', self.gf('django.db.models.fields.IntegerField')()),
            ('username', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal('requester', ['EmailAccount'])

        # Adding model 'ServerAccount'
        db.create_table('requester_serveraccount', (
            ('account_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['requester.Account'], unique=True, primary_key=True)),
            ('username', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('requester', ['ServerAccount'])

        # Adding model 'WebServerAccount'
        db.create_table('requester_webserveraccount', (
            ('serveraccount_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['requester.ServerAccount'], unique=True, primary_key=True)),
            ('url', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('requester', ['WebServerAccount'])

        # Adding model 'FTPServerAccount'
        db.create_table('requester_ftpserveraccount', (
            ('serveraccount_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['requester.ServerAccount'], unique=True, primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('requester', ['FTPServerAccount'])

        # Adding model 'Satellite'
        db.create_table('requester_satellite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('identification', self.gf('django.db.models.fields.TextField')()),
            ('request_server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requester.WebServerAccount'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('requester', ['Satellite'])

        # Adding model 'Channel'
        db.create_table('requester_channel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('in_file', self.gf('django.db.models.fields.TextField')(null=True, db_index=True)),
            ('satellite', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requester.Satellite'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('requester', ['Channel'])

        # Adding model 'AutomaticDownload'
        db.create_table('requester_automaticdownload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requester.Area'])),
            ('time_range', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requester.UTCTimeRange'])),
            ('email_server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requester.EmailAccount'])),
            ('root_path', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('requester', ['AutomaticDownload'])

        # Adding M2M table for field channels on 'AutomaticDownload'
        db.create_table('requester_automaticdownload_channels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('automaticdownload', models.ForeignKey(orm['requester.automaticdownload'], null=False)),
            ('channel', models.ForeignKey(orm['requester.channel'], null=False))
        ))
        db.create_unique('requester_automaticdownload_channels', ['automaticdownload_id', 'channel_id'])

        # Adding model 'Request'
        db.create_table('requester_request', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('automatic_download', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requester.AutomaticDownload'])),
            ('begin', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('requester', ['Request'])

        # Adding model 'Order'
        db.create_table('requester_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('request', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['requester.Request'], unique=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requester.FTPServerAccount'], null=True)),
            ('identification', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('downloaded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('requester', ['Order'])

        # Adding model 'File'
        db.create_table('requester_file', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requester.Order'])),
            ('localname', self.gf('django.db.models.fields.TextField')()),
            ('remotename', self.gf('django.db.models.fields.TextField')()),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('downloaded', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('begin_download', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('end_download', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('requester', ['File'])

        # Adding model 'GOESRequest'
        db.create_table('requester_goesrequest', (
            ('request_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['requester.Request'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('requester', ['GOESRequest'])


    def backwards(self, orm):
        # Deleting model 'Area'
        db.delete_table('requester_area')

        # Deleting model 'UTCTimeRange'
        db.delete_table('requester_utctimerange')

        # Deleting model 'Account'
        db.delete_table('requester_account')

        # Deleting model 'EmailAccount'
        db.delete_table('requester_emailaccount')

        # Deleting model 'ServerAccount'
        db.delete_table('requester_serveraccount')

        # Deleting model 'WebServerAccount'
        db.delete_table('requester_webserveraccount')

        # Deleting model 'FTPServerAccount'
        db.delete_table('requester_ftpserveraccount')

        # Deleting model 'Satellite'
        db.delete_table('requester_satellite')

        # Deleting model 'Channel'
        db.delete_table('requester_channel')

        # Deleting model 'AutomaticDownload'
        db.delete_table('requester_automaticdownload')

        # Removing M2M table for field channels on 'AutomaticDownload'
        db.delete_table('requester_automaticdownload_channels')

        # Deleting model 'Request'
        db.delete_table('requester_request')

        # Deleting model 'Order'
        db.delete_table('requester_order')

        # Deleting model 'File'
        db.delete_table('requester_file')

        # Deleting model 'GOESRequest'
        db.delete_table('requester_goesrequest')


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
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localname': ('django.db.models.fields.TextField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requester.Order']"}),
            'remotename': ('django.db.models.fields.TextField', [], {}),
            'size': ('django.db.models.fields.IntegerField', [], {})
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