#from django.db import models
from requester.models import *
from model_utils.managers import *
from decimal import Decimal

# Create your models here.

class ProcessManager(InheritanceManager):
	def all(self, *argc, **argv):
		return super(ProcessManager,self).all(*argc, **argv).select_subclasses()
	def filter(self, *argc, **argv):
		return super(ProcessManager,self).filter(*argc, **argv).select_subclasses()

class Process(models.Model):
	class Meta:
        	app_label = 'plumbing'
	objects = ProcessManager()
	name = models.TextField(db_index=True)
	description = models.TextField(db_index=True)
	progress = models.DecimalField(max_digits=5,decimal_places=2)
	executing = models.BooleanField()
	def __str__(self):
		return self.__class__.__name__ + ' [' + self.name + ']'

class ComplexProcess(Process):
	class Meta:
        	app_label = 'plumbing'
	processes = models.ManyToManyField('Process', through='ProcessOrder', related_name='complex_process')
	def do(self, data):
		self.progress = 0
		self.executing = True
		self.save()
		cache = data
		ps = self.processes.all().order_by('used_by__position')
		count = 0.0
		for subprocess in ps:
			cache = subprocess.do(cache)
			count += 1
			self.progress = (count / len(ps)) * 100
			self.save()
		self.executing = False
		self.save()
		return cache

class ProcessOrder(models.Model):
	class Meta:
        	app_label = 'plumbing'
	position = models.IntegerField()
	process = models.ForeignKey('Process', related_name='used_by')
	complex_process = models.ForeignKey(ComplexProcess)

class Program(ComplexProcess):
	class Meta:
        	app_label = 'plumbing'
	automatic_download = models.ForeignKey(AutomaticDownload)
	def downloaded_files(self):
		return [ f for request in self.automatic_download.request_set.all() for f in request.order.file_set.filter(downloaded=True).order_by('localname') ]
	def source(self):
		files = self.downloaded_files()
		files.sort()
		return { 'all': files }
	def execute(self):
		self.do(self.source())
