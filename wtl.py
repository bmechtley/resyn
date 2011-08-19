from pylab import *

import scipy.io.wavfile as wavfile
import argparse
import pywt

from mra import *
from visualization import *

# Find the greatest power of 2 less than or equal to an input value.
def lepow2(x): return 2 ** floor(log2(x))

#----------------------------------------------------#
# main: make a random permutation of an input sound. #
#----------------------------------------------------#

def main(sounds, wavelet):
	wavelet = pywt.Wavelet(wavelet)
	dwtmode = 'per'
	
	print wavelet
	
	for filename in sounds:
		fs, input = wavfile.read(filename)
		if input.ndim > 1: input = mean(input, 1)
		input = input[0:lepow2(len(input))]
		
		subplot(211)
		specgram(input)
		
		levels = int(log2(len(input))) + 1
		print filename, '\n\t%d samples, %d levels' % (len(input), levels)
		
		tree = MRATree(pywt.wavedec(input, wavelet, mode = dwtmode, level = levels))
		tree.tap(0.5)
		tree.printLevels(4)
		output_dwt = tree.untree()
		output = pywt.waverec(output_dwt, wavelet, mode = dwtmode)
		
		subplot(212)
		specgram(output)
		show()
		
		wavfile.write('%s-new.wav' % filename.split('.')[0], fs, int16(output))
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('sound', metavar='sound', type=str, 
		nargs='+', help='sounds to be resynthesized')
	parser.add_argument('-w', '--wavelet', 
		default = 'db5', choices = pywt.wavelist(), 
		required = False, metavar='wavelet', dest='wavelet',
		help = 'which wavelet to use in analysis/resynthesis')
	parser.add_argument('-v', dest='verbose', action='store_true',
		help = 'print verbose output')
		
	args = parser.parse_args()
	
	main(args.sound, args.wavelet)
	