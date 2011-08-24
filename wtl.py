from texture import *
import argparse

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

textures = [Texture(f) for f in args.sound]
	
for t in textures:
	tree = t.mra(args.wavelet, 'per')
	tree.tap(0.8, 0.01, 10)
	t.samples = tree.reconstruct()
	t.save('%s-new.wav' % t.file.split('.')[0])
