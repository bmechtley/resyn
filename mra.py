from pylab import *
from scipy.stats import scoreatpercentile
from random import choice
import pywt
import time

def identify_transients(input, p = 0.8):
	d = difference(sqrt(hilbert(input) ** 2 + input ** 2))
	threshold = scoreatpercentile(d, 0.8)
	return d > scoreatpercentile

class MRANode:
	"""
	MRA node object used by MRATree with links to ancestors and predecessors.
	
	Each MRA node represents a single coefficient of a multiresolution discrete
	wavelet transform.
	"""
	
	def __init__(self, value, parent, predecessor, side, level):
		self.value = value
		self.children = [None, None]
		self.parent = parent
		self.predecessor = predecessor
		self.level = level
		if self.parent is not None: self.parent.children[side] = self
	
	def __str__(self):
		return 'MRANode: %d, level %d' % (self.value, self.level)
	
	def childIndex(self):
		"""Return the index of this node in its parent's list of children."""
		
		return self.parent.children.index(self)
	
	def ancestors(self):
		"""Return a list of ancestors, going all the way to the root."""
		
		ancestor_list = []
		n = self
		
		while n.parent:
			ancestor_list.append(n.parent)
			n = n.parent
		
		return ancestor_list
	
	def predecessors(self, k = 2):
		"""Return a list of predecessors of length k."""
		
		predecessor_list = []
		n = self
		
		for i in range(0, k):
			predecessor_list.append(n.predecessor)
			n = n.predecessor
		
		return predecessor_list
	
	def adopt(self, n1, n2):
		"""Give up children and adopt two new ones (n1 and n2)."""
		
		self.children = [n1, n2]
		n1.parent = self
		n2.parent = self
	
class MRATree:
	"""
	Multiresolution analysis tree from constructed from a one-dimensional signal.
	
	An MRA tree is a binary tree where each node represents a DWT coefficient.
	Using a tree structure speeds up tree-based operations, as no data needs to be 
	copied and edges can be modified in-place.
	"""
	
	def __init__(self, input, wavelet = 'db5', mode = 'per'):
		self.root = None
		self.nodes = []
		self.wavelet = wavelet
		self.mode = mode
		t1 = time.time()
		self.dwt = pywt.wavedec(input, wavelet, mode = mode, level = int(log2(len(input))) + 1)
		print 'wavelet decomposition in', time.time() - t1, 'seconds.'
		parents = [None]
		t1 = time.time()
		for i in range(0, len(self.dwt)):
			nodes = []
			
			for j in range(0, len(self.dwt[i])):
				if j > 0:
					nodes.append(MRANode(self.dwt[i][j], parents[j / 2], nodes[j - 1], j % 2, i))
				else:
					nodes.append(MRANode(self.dwt[i][j], parents[j / 2], None, j % 2, i))
			
			nodes[0].predecessor = nodes[-1]
			parents = nodes
			self.nodes.extend(nodes)
			if i is 0: self.root = nodes[0]
		print 'tree construction in', time.time() - t1, 'seconds.'
		
	def reconstruct(self, node = None, level = 0, index = 0):
		"""
		Return a reconstructed one-dimensional signal from the MRA tree.
		
		node, level, index -- used internally for recursive breadth-first reconstruction.
		"""
		
		if node is None: node = self.root		
		self.dwt[level][index] = node.value
		
		map(
			lambda c:
				self.reconstruct(c, level + 1, index * 2 + c.parent.children.index(c))
				if c else None,
			node.children
		)
		
		if not level: return pywt.waverec(self.dwt, self.wavelet, mode = self.mode)
	
	def shake(self, node = None, level = 0, maxlevel = -1):
		"""
		Randomly swap children for every node.
		
		node, level -- used internally for recursive depth-first traversal.
		maxlevel -- level at which to stop swapping children.
		"""
		
		if maxlevel < 0 or level < maxlevel:
			if not node: node = self.root
			if len(node.children) and node.children[0] and node.children[1]:
				shuffle(node.children)
			for child in [c for c in node.children if c != None]:
				self.shake(child, level + 1, maxlevel)
	
	def ascore(self, c, nancestors, threshold):
		"""
		Return wavelet tree learning ancestor similarity score.
		
		c -- candidate node in question.
		nancestors -- list of the original node's ancestors (MRANode instances).
		threshold -- value under which two paths are considered similar. 
		"""
		
		cancestors = array([p.value for p in c.ancestors()])
		ascores = abs(nancestors - cancestors)
		ascores /= linspace(1, len(ascores), len(ascores))
		return sum(cumsum(ascores) < threshold)
		
	def pscore(self, c, npredecessors, nk, threshold):
		"""Return wavelet tree learning predecessor similarity score.
		
		c -- candidate node in question.
		npredecessors -- list of the original node's predecessors.
		nk -- number of predecessors to consider.
		threshold -- value under which two paths are considered similar.
		"""
		
		cpredecessors = array([p.value for p in c.predecessors(nk)])
		pscores =  abs(npredecessors - cpredecessors)
		return sum(cumsum(pscores) < threshold)
	
	def tap(self, p = 0.8, k = 0.01, maxlevel = -1):
		"""
		Rearrange tree using wavelet tree learning as per TAPESTREA.
		
		p -- what percentage of nodes to consider for the threshold. 
			Larger values result in more variation.
		k -- number of predecessors to consider in comparing node contexts.
			Smaller values will tend to break up longer events.
		maxlevel -- maximum level at which to rearrange nodes. Oftentimes
			10 is sufficient. Use -1 (default) to rearrange all levels.
			Note that children of rearranged nodes will be moved around
			regardless.
		"""
		
		t1 = time.time()
		
		threshold = scoreatpercentile([abs(n.value) for n in self.nodes], p * 100) * 2.0
		parents = array([])
		children = array([self.root])
		
		while len(children) > 0:
			nodes = children.copy()
			new_nodes = nodes.copy()
			level = nodes[0].level
			
			if level > 2 and (level < maxlevel or maxlevel < 0):				
				nk = int(k * 2 ** level)
				
				# Choose new node ordering.
				for i in range(0, len(nodes)):
					nancestors = array([p.value for p in nodes[i].ancestors()])
					npredecessors = array([p.value for p in nodes[i].predecessors(nk)])
					
					ascores = array([self.ascore(c, nancestors, threshold) for c in nodes])
					pscores = array([self.pscore(c, npredecessors, nk, threshold) for c in nodes])
					
					candidates = nodes[(ascores == max(ascores)) & (pscores == max(pscores))]
					selection = choice(candidates)
					new_nodes[i] = selection
				
				# Fix predecessor relationships.
				for i in range(0, len(new_nodes)):
					new_nodes[i].predecessor = new_nodes[i - 1]
				
				# Fix parent/child relationships.
				for i in range(0, len(parents)):
					parents[i].adopt(new_nodes[i * 2], new_nodes[i * 2 + 1])
			
			parents = nodes
			children = array([c for c in array([n.children for n in nodes]).flat if c != None])
			
		print 'tapped in', (time.time() - t1), 'seconds or less.'
