from pylab import *
from scipy.stats import scoreatpercentile
from random import choice

#-----------------------------------------------------------------------------#
# MRANode/MRATree:															  #
#	These classes set up a tree for multiresolution analysis from dwt output. #
#	This speeds up tree-based operations quite a bit, as no data needs to be  #
#	copied and the trees can be modified in place.							  #
#-----------------------------------------------------------------------------#

class MRANode:
	def __init__(self, value, parent, predecessor, side, level):
		self.value = value
		self.children = [None, None]
		self.children2 = [None, None]
		self.parent = parent
		self.predecessor = predecessor
		self.predecessor2 = None
		self.parent2 = None
		self.level = level
		if self.parent is not None: self.parent.children[side] = self
	
	def childIndex(n):
		return self.parent.children.index(self)
	
	def __cmp__(self, other):
		if other != None: return self.value - other.value
		else: return 1
	
	def __str__(self):
		return str(id(self))#'MRANode: %d, level %d' % (self.value, self.level)
	
class MRATree:
	def __init__(self, input):
		self.root = None
		self.nodes = []
		self.data = input
		
		parents = [None]
		
		for i in range(0, len(input)):
			nodes = [
				MRANode(input[i][j], parents[j / 2], input[i][j - 1], j % 2, i)
				for j in range(0, len(input[i]))
			]
			parents = nodes
			self.nodes.extend(nodes)
			if i is 0: self.root = nodes[0]
	
	#-----------------------------------------------------------------------------#
	# printLevels: print the tree in order of predecessors up to a certain level. #
	#-----------------------------------------------------------------------------#
	
	def printLevels(self, maxlevel = -1, nodes = []):
		if maxlevel < 0: maxlevel = max([n.level for n in self.nodes])
		if not len(nodes): nodes = [self.root]
		print 'Level %d:' % nodes[0].level, ', '.join([str(n) for n in nodes])
		
		if maxlevel <= nodes[0].level: return
		else: self.printLevels(maxlevel, [n for n in list(flatten([n.children for n in nodes])) if n != None])
	
	#--------------------------------------------------------------#
	# untree: convert tree to DWT format acceptable by PyWavelets. #
	#--------------------------------------------------------------#
	
	def untree(self, node = None, level = 0, index = 0):
		if node is None: node = self.root		
		
		self.data[level][index] = node.value
		
		map(
			lambda c:
				self.untree(c, level + 1, index * 2 + c.parent.children.index(c))
				if c else None,
			node.children
		)
		
		if not level: return self.data
	
	#-----------------------------------------------#
	# shake: randomly swap children for every node. #
	#-----------------------------------------------#
	
	def shake(self, node = None, level = 0, maxlevel = -1):
		if maxlevel < 0 or level < maxlevel:
			if not node: node = self.root
			if len(node.children) and node.children[0] and node.children[1]:
				shuffle(node.children)
			for child in [c for c in node.children if c != None]:
				self.shake(child, level + 1, maxlevel)
	
	#----------------------------------------------#
	# tap: wavelet tree learning as per TAPESTREA. #
	#----------------------------------------------#
	
	def tap(self, p = 0.2):
		threshold = scoreatpercentile([n.value for n in self.nodes], p)
		
		parents = []
		nodes = [self.root]
		
		while len(nodes) > 0:
			candidates = nodes[:]					# Nodes from which to choose randomly.
			shuffle(candidates)
			new_nodes = candidates[:]				# New ordering of nodes on this level.
			
			if len(new_nodes) > 1:
				# Create new ordering.
				for i in range(0, len(new_nodes)):
					new_nodes[i] = candidates.pop()
				
				# Re-assign predecessor relationships.
				for i in range(0, len(new_nodes)):
					new_nodes[i].predecessor = new_nodes[i - 1]
				
				# Re-assign parent/child relationships.
				node_stack = new_nodes[:]
				
				for p in parents:
					for i in range(0, len(p.children)):
						if len(node_stack):
							p.children[i] = node_stack.pop()
							p.children[i].parent = p
							
			parents = new_nodes[:]
			nodes = [n for n in list(flatten([n.children for n in new_nodes])) if n != None]
	