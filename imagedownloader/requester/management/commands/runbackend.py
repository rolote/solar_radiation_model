from django.core.management.base import BaseCommand
from requester.models_goes import *
import signal
import sys


class Command(BaseCommand):
	args = '<worker_quantity>'
	help = 'Run the background process that download the active AutomaticDownload instances.'
	def __init__(self, *args, **options):
		super(Command, self).__init__()

	def handle(self, *args, **options):
		quantity = int(args[0]) if len(args) > 0 else 8
		self.background = WorkerManager(quantity)
		self.background.put_job(QOSManager())
		print 'Press Ctrl+C'
		try:
			self.background.start_workers()
		except KeyboardInterrupt:
    			print 'You pressed Ctrl+C!'
			self.background.stop_workers()
   			sys.exit(0)
