# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'OpticFilter'
        db.create_table('station_opticfilter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(db_index=True)),
        ))
        db.send_create_signal('station', ['OpticFilter'])

        # Adding model 'Brand'
        db.create_table('station_brand', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(db_index=True)),
        ))
        db.send_create_signal('station', ['Brand'])

        # Adding model 'Product'
        db.create_table('station_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('brand', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['station.Brand'])),
        ))
        db.send_create_signal('station', ['Product'])

        # Adding model 'Sensor'
        db.create_table('station_sensor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('serial_number', self.gf('django.db.models.fields.IntegerField')()),
            ('optic_filter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['station.OpticFilter'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['station.Product'])),
        ))
        db.send_create_signal('station', ['Sensor'])

        # Adding model 'Position'
        db.create_table('station_position', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=7)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=7)),
        ))
        db.send_create_signal('station', ['Position'])

        # Adding model 'Station'
        db.create_table('station_station', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('position', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['station.Position'])),
        ))
        db.send_create_signal('station', ['Station'])

        # Adding model 'Configuration'
        db.create_table('station_configuration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('frequency', self.gf('django.db.models.fields.TimeField')()),
            ('frequency_save', self.gf('django.db.models.fields.TimeField')()),
            ('calibration_value', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=4)),
            ('sensor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['station.Sensor'])),
            ('position', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['station.Position'])),
            ('multiplier', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal('station', ['Configuration'])

        # Adding model 'Measure'
        db.create_table('station_measure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('configuration', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['station.Configuration'])),
        ))
        db.send_create_signal('station', ['Measure'])

        # Adding model 'Datalogger'
        db.create_table('station_datalogger', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.TextField')(db_index=True)),
        ))
        db.send_create_signal('station', ['Datalogger'])

        # Adding model 'Channel'
        db.create_table('station_channel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('datalogger', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['station.Datalogger'])),
        ))
        db.send_create_signal('station', ['Channel'])

        # Adding model 'StaticConfiguration'
        db.create_table('station_staticconfiguration', (
            ('configuration_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['station.Configuration'], unique=True, primary_key=True)),
            ('angle', self.gf('django.db.models.fields.DecimalField')(max_digits=4, decimal_places=2)),
        ))
        db.send_create_signal('station', ['StaticConfiguration'])

        # Adding model 'Difuse'
        db.create_table('station_difuse', (
            ('staticconfiguration_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['station.StaticConfiguration'], unique=True, primary_key=True)),
            ('shadow_ball', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('station', ['Difuse'])

        # Adding model 'Global'
        db.create_table('station_global', (
            ('staticconfiguration_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['station.StaticConfiguration'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('station', ['Global'])

        # Adding model 'Direct'
        db.create_table('station_direct', (
            ('configuration_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['station.Configuration'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('station', ['Direct'])


    def backwards(self, orm):
        # Deleting model 'OpticFilter'
        db.delete_table('station_opticfilter')

        # Deleting model 'Brand'
        db.delete_table('station_brand')

        # Deleting model 'Product'
        db.delete_table('station_product')

        # Deleting model 'Sensor'
        db.delete_table('station_sensor')

        # Deleting model 'Position'
        db.delete_table('station_position')

        # Deleting model 'Station'
        db.delete_table('station_station')

        # Deleting model 'Configuration'
        db.delete_table('station_configuration')

        # Deleting model 'Measure'
        db.delete_table('station_measure')

        # Deleting model 'Datalogger'
        db.delete_table('station_datalogger')

        # Deleting model 'Channel'
        db.delete_table('station_channel')

        # Deleting model 'StaticConfiguration'
        db.delete_table('station_staticconfiguration')

        # Deleting model 'Difuse'
        db.delete_table('station_difuse')

        # Deleting model 'Global'
        db.delete_table('station_global')

        # Deleting model 'Direct'
        db.delete_table('station_direct')


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
        'station.difuse': {
            'Meta': {'object_name': 'Difuse', '_ormbases': ['station.StaticConfiguration']},
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