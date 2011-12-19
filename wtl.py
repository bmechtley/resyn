from texture import *
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('sound',
	metavar = 'sound',
	nargs = '+',
	help = 'sounds to be resynthesized')
parser.add_argument('-w', '--wavelet',
	default = 'db5',
	metavar = 'wavelet',
	help = 'which wavelet to use in analysis/resynthesis')
parser.add_argument('-k',
	default = 0.01,
	type = float,
	metavar = 'predecessors',
	help = 'number of predecessors to consider in percentage of the total sound length.')
parser.add_argument('-p',
	default = 0.8,
	type = float,
	metavar = 'percentile',
	help = 'percentage of wavelet coefficients to consider in setting WTL threshold.')
parser.add_argument('-l',
	default = 10,
	metavar = 'level',
	type = int,
	help = 'maximum level to permute')
parser.add_argument('-o', '--output',
	default = None,
	metavar = 'filename',
	help = 'where to store the resulting file')
parser.add_argument('-v', '--verbose',
	dest = 'verbose',
	action = 'store_true',
	help = 'print verbose output')

args = parser.parse_args()

textures = [Texture(f) for f in args.sound]

for t in textures:
	t.tap(args.p, args.k, args.l)
	t.save(args.output if args.output else '%s-new.wav' % t.file.split('.')[0])
