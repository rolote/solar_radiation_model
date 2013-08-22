# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Difuse'
        db.delete_table('station_difuse')

        # Adding model 'Diffuse'
        db.create_table('station_diffuse', (
            ('staticconfiguration_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['station.StaticConfiguration'], unique=True, primary_key=True)),
            ('shadow_ball', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('station', ['Diffuse'])


    def backwards(self, orm):
        # Adding model 'Difuse'
        db.create_table('station_difuse', (
            ('staticconfiguration_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['station.StaticConfiguration'], unique=True, primary_key=True)),
            ('shadow_ball', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('station', ['Difuse'])

        # Deleting model 'Diffuse'
        db.delete_table('station_diffuse')


    models = {
        'station.brand': {
            'Meta': {'object_name': 'Brand'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        'station.channel': {
            'Meta': {'object_name': 'Channel'},
            'datalogger': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['station.Datalogger']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        'station.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'calibration_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '4'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'frequency': ('django.db.models.fields.TimeField', [], {}),
            'frequency_save': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multiplier': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'position': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['station.Position']"}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['station.Sensor']"})
        },
        'station.datalogger': {
            'Meta': {'object_name': 'Datalogger'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        'station.diffuse': {
            'Meta': {'object_name': 'Diffuse', '_ormbases': ['station.StaticConfiguration']},
            'shadow_ball': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'staticconfiguration_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['station.StaticConfiguration']", 'unique': 'True', 'primary_key': 'True'})
        },
        'station.direct': {
            'Meta': {'object_name': 'Direct', '_ormbases': ['station.Configuration']},
            'configuration_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['station.Configuration']", 'unique': 'True', 'primary_key': 'True'})
        },
        'station.global': {
            'Meta': {'object_name': 'Global', '_ormbases': ['station.StaticConfiguration']},
            'staticconfiguration_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['station.StaticConfiguration']", 'unique': 'True', 'primary_key': 'True'})
        },
        'station.measure': {
            'Meta': {'object_name': 'Measure'},
            'configuration': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['station.Configuration']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'})
        },
        'station.opticfilter': {
            'Meta': {'object_name': 'OpticFilter'},
            'description': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        'station.position': {
            'Meta': {'object_name': 'Position'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '7'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '7'})
        },
        'station.product': {
            'Meta': {'object_name': 'Product'},
            'brand': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['station.Brand']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        'station.sensor': {
            'Meta': {'object_name': 'Sensor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'optic_filter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['station.OpticFilter']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['station.Product']"}),
            'serial_number': ('django.db.models.fields.IntegerField', [], {})
        },
        'station.staticconfiguration': {
            'Meta': {'object_name': 'StaticConfiguration', '_ormbases': ['station.Configuration']},
            'angle': ('django.db.models.fields.DecimalField', [], {'max_digits': '4', 'decimal_places': '2'}),
            'configuration_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['station.Configuration']", 'unique': 'True', 'primary_key': 'True'})
        },
        'station.station': {
            'Meta': {'object_name': 'Station'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'position': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['station.Position']"})
        }
    }

    complete_apps = ['station']