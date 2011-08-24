from pylab import *
import pywt

def specs(textures, crop = True):
	"""
	Plot stacked spectrograms for each several sound textures.
	
	textures -- a list of Texture instances.
	crop -- toggle cropping spectrograms to the minimum duration amongst the textures.
	"""
	
	minduration = min([len(t.samples) / t.fs for t in textures])
	
	for i in range(0, len(textures)):
		subplot(len(textures), 1, i)
		samples = textures[i].samples[0:minduration * textures[i].fs] if crop else textures[i].samples
		specgram(samples, Fs = textures[i].fs)
		title(textures[i].file.split('/')[-1])
		if i is 0: xlabel('Time (s)')
		else: xticks([])
		ylabel('Frequency (Hz)')
		
	show()

def scalogram(tree, scaling = True, levels = None):	
	"""
	Plot a scalogram for PyWavelets DWT output.
	
	scaling -- toggles on power-of-2 height scaling per level.
	levels -- maximum number of levels to plot.
	"""
	
	bottom = 0
	if not levels: levels = len(tree)
	
	vmin = min(map(lambda x: min(x**2), tree))
	vmax = max(map(lambda x: max(x**2), tree))
	
	gca().set_autoscale_on(False)
	
	for i in range(1, levels):
		scale = 2.0 ** (i - levels) if scaling else 1.0 / levels
		
		imshow(abs(array([tree[i] ** 2])),
			interpolation = 'bilinear', 
			vmin = vmin, 
			vmax = vmax,
			extent = [0, 1, bottom, bottom + scale],
			aspect = 1)
			
		bottom += scale

# Wavelet packet decomposition scalogram.
def packet_scalogram(signal, wavelet = pywt.Wavelet('db5'), mode = 'ppd', order = 'freq', fs = 44100):
	"""
	Plot a wavelet packet decomposition (WPD) scalogram.
	
	signal -- the one-dimensional signal to use for the scalogram.
	wavelet -- the wavelet to use. This is an element of pywt.wavelist()
	mode -- the wavelet extension mode to use for boundaries.
	order -- how to order the nodes in the scalogram.
	fs -- samplerate of the signal for plotting axes.
	"""
	
	levels = pywt.dwt_max_level(len(signal), wavelet.dec_len) / 2
	
	wp = pywt.WaveletPacket(signal, wavelet, mode, maxlevel = levels)
	nodes = wp.get_level(levels, order = order)
	values = abs(array([n.data for n in nodes]))
	
	for i in range(0, len(values)):
		values[i,:] = values[i,:] ** 2
		values[i,:] *= 2**(i / 128.0)
		#values[i,:] = sqrt(values[i,:])
	
	imshow(values, 
		interpolation = 'bilinear', 
		aspect = 'auto', 
		origin = 'lower',
		extent = [0, 1, 0, len(values)])
