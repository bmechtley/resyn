from scipy.io import wavfile
from stft import *
from mra import *

#-------------------------------------------------------#
# Texture: sound texture class for messing with sounds. #
#-------------------------------------------------------#

class Texture:
	"""
	Mono sound texture class for messing with sounds. Simple I/O.
	
	Currently, this is a simple wrapper that contains an MRA tree, but in the future, methods that 
	do not use an MRA tree may be included.
	"""
	
	def __init__(self, file, wavelet = 'db5', mode = 'per', analyze = True):
		self.file = file
		self.fs, self.samples = wavfile.read(file)
		self.fs = float(self.fs)
		if self.samples.ndim > 1: self.samples = mean(self.samples, 1)
		
		if analyze:
			self.mra = MRATree(self.samples[0:2 ** self.max_levels()], wavelet, mode = mode)
			self.stft = STFT(self.samples, self.fs, 0.02, 0.01)
		
	def __str__(self):
		return '%s (%f s, %d Hz, %d samples)' % (self.file, len(self.samples) / self.fs, self.fs, len(self.samples))
	
	def plotSpecgram(self, ticks = True):
		"""Plot a spectrogram with correct axes."""
				
		specgram(self.samples, Fs = self.fs)
		xlim(0, len(self.samples) / self.fs)
		ylim(0, self.fs / 2)
		if not ticks: gca().set_xticklabels([])
		else: xlabel('Time (s)')
		ylabel('Frequency (kHz)')
		yticks([0,5000,10000,15000,20000], ['0', '5', '10', '15', '20'])
				
	def plotFeatures(self):
		"""Plot STFT features with correct axes."""
		
		l = self.stft.loudness()
		c = self.stft.centroid()
		
		plot(c / max(c))
		xticks([])
		yticks([])
		xlim(0, len(c))
		
	def save(self, filename):
		"""Write the mono sound to disk."""
		
		wavfile.write(filename, self.fs, int16(self.samples))
	
	#---------------#
	# MRA features. #
	#---------------#
	
	def max_levels(self):
		"""Return the maximum number of MRA tree levels."""
		
		return floor(log2(len(self.samples)))
	
	def tap(self, p = 0.8, k = 0.01, maxlevel = -1):
		"""Perform wavelet tree learning."""
		
		self.mra.tap(p, k, maxlevel)
		self.samples = self.mra.reconstruct()
	
	def shake(self, maxlevel = -1):
		"""Perform random child swapping."""
		
		self.mra.shake(maxlevel = maxlevel)
		self.samples = self.mra.reconstruct()
