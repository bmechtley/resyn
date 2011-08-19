from pylab import *
import pywt

# Plot a scalogram in the current axes. Scaling turns on power of 2 height scaling per level.	
def scalogram(tree, scaling = True, levels = None):	
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
