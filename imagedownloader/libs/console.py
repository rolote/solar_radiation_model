import sys
import pyttsx

engine = pyttsx.init()

def show(*objs):
	begin = '' if '\r' in objs[0] or '\b' in objs[0] else '\n'
	sys.stdout.write(begin)
	for part in objs:
		sys.stdout.write(str(part))
	sys.stdout.flush()

def say(speech):
	#NOT engine.startLoop()
	show(speech)
	engine.say(speech)
	engine.runAndWait()

progress = ['/','-','\\','|']
def show_progress(i):
	show('\b \b', progress[i % len(progress)])

