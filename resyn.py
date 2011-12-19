import matplotlib
matplotlib.use('TkAgg')

import argparse
from texture import *
from matplotlib.widgets import Slider, Button, RadioButtons, SpanSelector
import pyaudio
from scipy.signal import hilbert
from pylab import *

pa = pyaudio.PyAudio()

class TexturePlot():
	def __init__(self, filename, i, n, widgets, analyze = True):
		self.filename = filename
		self.t = Texture(filename, analyze = analyze)
		self.t.samples = self.t.samples[0:2 ** self.t.max_levels()]
		self.p = 1.0 - (40.0 / len(self.t.samples))
		self.lines = []
		
		self.calculateTransients(self.p)
		
		spacing = 0.05
		bottom = len(widgets) * spacing + 3 * spacing
		height = (1.0 - bottom) / n - spacing / 4
		
		
		self.box = [
			0.2, 
			bottom + (i * spacing) + height * i,
			0.6, 
			height - spacing * n
		]
		self.spec = axes(self.box)
		self.overlay = axes(self.box, frameon = False)
		self.overlay.set_xticklabels([])
		self.overlay.set_yticklabels([])
		
		self.buttons = [
			{'name': 'tap', 'function': self.tap},
			{'name': 'shake', 'function': self.shake},
			{'name': 'reset', 'function': self.reset},
			{'name': 'save', 'function': self.save}
		]
		
		for b in range(0, len(self.buttons)):
			self.buttons[b]['axes'] = axes([0.85, self.box[1] + b * self.box[3] / len(self.buttons), 0.1, 0.05])
			self.buttons[b]['button'] = Button(self.buttons[b]['axes'], self.buttons[b]['name'])
			self.buttons[b]['button'].on_clicked(self.buttons[b]['function'])
		
		self.span = SpanSelector(self.overlay, self.play, 'horizontal', rectprops=dict(alpha=0.5, facecolor='red') )
		
		self.i = i
		self.n = n
		
		self.widgets = widgets
		self.replot()
	
	def calculateTransients(self, alpha = 0.9999, beta = 0.0001):
		print '\ttransients'
		d = self.t.samples.copy()
			
		for i in range(1, len(d)):
			if d[i - 1] < self.t.samples[i]:
				d[i] = beta * d[i - 1] + (1 - beta) * self.t.samples[i]
			else:
				d[i] = alpha * d[i - 1] + (1 - alpha) * self.t.samples[i]
		
		d = diff(d)
		threshold = scoreatpercentile(d, self.p * 100)
		self.marks = (array(d) > threshold).nonzero()[0]
		print '\tdone'
		
	def replot(self):
		sca(self.spec)
		self.t.plotSpecgram()
		
		if len(self.marks):
			sca(self.overlay)
			
			while(len(self.lines)):
				self.lines.pop(0).remove()
			
			xlim(0, len(self.t.samples))
			for x in self.marks:
				self.lines.append(axvline(x, color = 'k'))
		
		draw()
	
	def play(self, xmin, xmax):
		stream = pa.open(format = pyaudio.paInt16, channels = 1, rate = int(self.t.fs), output = 1)	
		stream.write(self.t.samples[xmin:xmax].astype(int16).tostring())
		stream.close()
	
	def tap(self, e):
		print 'tapping'
		self.t.tap(self.widgets['p'].val, self.widgets['k'].val, self.widgets['l'].val)
		self.calculateTransients(self.p)
		print 'done'
		self.replot()
	
	def shake(self, e):
		print 'shaking'
		self.t.shake(self.widgets['l'].val)
		self.calculateTransients(self.p)
		print 'done'
		self.replot()
	
	def save(self, e):
		print 'saving'
		self.t.save(self.filename.split('.')[0] + '-itap.wav')
		print 'done'
		
	def reset(self, e):
		print 'resetting'
		self.t = Texture(self.filename)
		self.t.samples = self.t.samples[0:2 ** self.t.max_levels()]
		self.calculateTransients(self.p)
		print 'done'
		self.replot()
	
class TextureControls:
	def __init__(self, filenames):
		widgets = {
			'p': Slider(axes([0.2, 0.15, 0.6, 0.025]), 'p',	0, 1.0, valinit = 0.80,	valfmt = '%.2f%%'),
			'k': Slider(axes([0.2, 0.1, 0.6, 0.025]), 'k', 0, 1.0, valinit = 0.01,	valfmt = '%.2f%%'),
			'l': Slider(axes([0.2, 0.05, 0.6, 0.025]), 'levels', 0, 20,	valinit = 10.0,	valfmt = '%d')
		}
		
		self.textures = []
		for i in range(0, len(filenames)):
			self.textures.append(TexturePlot(filenames[i], i, len(filenames), widgets, True))
		
		show()
	
parser = argparse.ArgumentParser()
parser.add_argument('sound', metavar = 'sound',	nargs = '+', help = 'sound to be resynthesized')
tc = TextureControls(parser.parse_args().sound)
