from django.db import models
from decimal import Decimal
from datetime import datetime, timedelta


# Create your models here.

class OpticFilter(models.Model):
	name = models.TextField(db_index=True)
	description = models.TextField(db_index=True)

	def __str__(self):
            return self.name

class Brand(models.Model):
	name = models.TextField(db_index=True)
	
	def __str__(self):
            return self.name

class Product(models.Model):
	name = models.TextField(db_index=True)
	brand = models.ForeignKey(Brand)

	def __str__(self):
            return self.name

class Sensor(models.Model):
	serial_number = models.IntegerField()
	optic_filter = models.ForeignKey(OpticFilter)
	product = models.ForeignKey(Product)
	
        def sensor_pretty_name(self):
            return '%i %s %s' % (self.serial_number, self.optic_filter.name, self.product.name) 

        def __str__(self):
            return str(self.serial_number)
	
class Position(models.Model):
	latitude = models.DecimalField(max_digits=10,decimal_places=7)
	longitude = models.DecimalField(max_digits=10,decimal_places=7)

        def coordinates(self):
            return '(%2f, %2f)' %  (self.latitude, self.longitude)

        def __str__(self):
            return self.coordinates()


class Station(models.Model):
	name = models.TextField(db_index=True)
	position = models.ForeignKey(Position)

        def __str__(self):
            return self.name
        def coordinates(self):
            return self.position.coordinates()


class Configuration(models.Model):
	datetime = models.DateTimeField()
	frequency = models.TimeField()          
	frequency_save = models.TimeField()
	calibration_value = models.DecimalField(max_digits=7,decimal_places=4)
	sensor = models.ForeignKey(Sensor)
        position = models.ForeignKey(Position)
        multiplier = models.DecimalField(max_digits=5,decimal_places=2)

class Measure(models.Model):
	value = models.DecimalField(max_digits=5,decimal_places=2)
	date = models.DateTimeField()
	configuration = models.ForeignKey(Configuration)

class Datalogger(models.Model):
	label = models.TextField(db_index=True)

	def __str__(self):
            return self.label

class Channel(models.Model):
	name = models.TextField(db_index=True)

	datalogger = models.ForeignKey(Datalogger)
	def __str__(self):
            return self.name

class StaticConfiguration(Configuration):
	angle = models.DecimalField(max_digits=4,decimal_places=2)

class Diffuse(StaticConfiguration):
	shadow_ball = models.BooleanField()

class Global(StaticConfiguration):
	pass

class Direct(Configuration):
	pass

