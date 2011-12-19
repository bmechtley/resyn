from visualization import *
from texture import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sound', metavar='sound', type=str, 
	nargs='+', help='sounds to plotted')
parser.add_argument('-c', dest='crop', action='store_true',
	help = 'crop sound lengths to minimum length')
args = parser.parse_args()

specs([Texture(f) for f in args.sound], args.crop)

show()
