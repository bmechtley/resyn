from pylab import *

def hz_to_bark(hz):
	return 6 * arcsinh(hz / 600)

class STFT:
	def __init__(self, input, fs, framesize, hopsize):
		self.samples = input
		self.fs = fs
		self.nfft = int(framesize * fs)
		self.nhop = int(hopsize * fs)
		self.npad = 2 ** (int(log2(self.nfft)) + 1)
		
		self.pxx, self.freqs, self.times = mlab.specgram(
			self.samples,
			self.nfft,
			self.fs,
			noverlap = self.nhop,
			pad_to = self.npad
		)
		
		print 'fs', self.fs
		print 'nfft', self.nfft
		print 'nhop', self.nhop
		print 'npad', self.npad
		
		# Spectral centroid initialization.
		self.bark_units = map(lambda i: hz_to_bark((self.fs * i) / (2 * (self.nfft - 1))), range(0, self.npad / 2))
		self.bark_weights = diff(self.bark_units)
	
	def loudness(self):
		return log10(sum(self.pxx * self.pxx, 0)) / self.pxx.shape[0]
	
	def centroid(self):
		print self.pxx[2:,:].shape
		print self.bark_weights.shape
		
		weighted = sum(self.pxx[2:,:] * self.pxx[2:,:] * self.bark_weights, 0)
		return sum(weighted * units[1:], 0) / sum(weighted, 0)
	
	def sparsity(self):
		return max(self.pxx, 0) / sum(self.pxx, 0)
	