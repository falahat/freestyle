
MAX_DISTANCE = float("inf")

# TODO: Optemize this and memoize
class WordGraphLazy(object):
	def __init__(self, phonetic_db, ngram_db):
		self.phonetic_db = phonetic_db
		self.ngram_db = ngram_db

	def children(self, node):
		result = []
		# TODO: might want to return edges in a sorted order? Perhaps even yield?
		for next_word, edge_probability in self.ngram_db.find_next(node.word):
			if next_word not in self.phonetic_db.phones:
				continue
			num_syllables_left = node.syllables_left - self.phonetic_db.num_syllables[next_word]
			next_node = WordNode(next_word, num_syllables_left)
			if self.is_node_valid(next_node):
				result.append(next_node) # TODO: Make a set?
		return result

	def distance(self, node1, node2):
		children = self.children(node1)
		word2 = node2.word
		for word, count in children:
			if word == word2:
				return 1 - count
		return MAX_DISTANCE
	
	def is_node_valid(self, node):
		return node.word in self.phonetic_db.phones and node.word in self.phonetic_db.num_syllables and node.syllables_left >= 0;

class WordGraph(WordGraphLazy):
	def __init__(self, phonetic_db, ngram_db, root_node):
		super(WordGraph, self).__init__(phonetic_db, ngram_db)
		self.root_node = root_node
		self.vertices = {self.root_node}

	def populate_graph(self):
		# We know this is a DAG, so we can take liberties?
		to_visit = {self.root_node}
		while (to_visit):
			curr_node = to_visit.pop()
			print(len(to_visit), len(self.vertices))
			if not self.is_node_valid(curr_node):
				continue # Unfortunately, we have to ignore the next words, even if we do have phonetic entries for them
			next_nodes = self.children(curr_node)
			self.vertices.update(next_nodes)
			to_visit.update(next_nodes)
	
	def distance(self, node1, node2):
		# TODO: Hella ineffecient
		children = self.children(node1)
		word2 = node2.word
		for word, count in children:
			if word == word2:
				return 1 - count
		return MAX_DISTANCE
	
	def search_nodes(self, desired_word=None, desired_rhyme=None, desired_syllables_left=None):
		# TODO: effeciently query the nodes. Possibly generate on demand?
		pass;

class TargetedGraph(WordGraph):
	def __init__(self, phonetic_db, ngram_db, num_desired_syllables, destination_nodes):
		super(TargetedGraph, self).__init__(phonetic_db, ngram_db, None)
		self.num_desired_syllables = num_desired_syllables
		self.destination_nodes = destination_nodes
		self.distance_from_dest = {node : 0 for node in destination_nodes}
		self.next_nodes = dict()
	
	def populate_graph(self):
		# TODO: Extract this out to at least 3 different helper methods
		to_visit = set(self.destination_nodes)
		while (to_visit):
			curr_node = to_visit.pop()
			if not self.is_node_valid(curr_node):
				continue # Unfortunately, we have to ignore the next words, even if we do have phonetic entries for them
			if curr_node.syllables_left == self.num_desired_syllables:
				yield self.trace_to_dest(curr_node)

			num_syllables_left = curr_node.syllables_left + self.phonetic_db.num_syllables[curr_node.word]
			for prev_node, possible_dist in self.previous_edges(curr_node):
				if self.distance_from_dest.get(prev_node, MAX_DISTANCE) > possible_dist:
					self.distance_from_dest[prev_node] = possible_dist
					self.next_nodes[prev_node] = curr_node
				to_visit.add(prev_node)
	
	def previous_edges(self, node):			
		num_syllables_left = node.syllables_left + self.phonetic_db.num_syllables[node.word]
		for prev_word, edge_probability in sorted(self.ngram_db.find_previous(node.word), key=lambda (w,p) : p):
			prev_node = WordNode(prev_word, num_syllables_left)
			if not self.is_node_valid(prev_node):
				continue
			possible_dist = self.distance_from_dest.get(node, MAX_DISTANCE) + (1 - edge_probability)
			yield prev_node, possible_dist

	def trace_to_dest(self, start_node):
		print("\n")
		result = []
		curr_node = start_node
		while curr_node is not None:
			result.append(curr_node.word)
			curr_node = self.next_nodes.get(curr_node, None)
		print(" ".join(result))
		return result

	def is_node_valid(self, node):
		if super(TargetedGraph, self).is_node_valid(node):
			if node.syllables_left == 0:
				return node in self.destination_nodes
			return True
		return False

class WordNode(object):
	def __init__(self, word, syllables_left):
		self.word = word
		self.syllables_left = syllables_left

	def __str__(self):
		return "({}, {})".format(self.word, self.syllables_left)

	def __repr__(self):
		return "WordNode({}, {})".format(self.word, self.syllables_left)

	def __eq__(self, other):
		return other.word == self.word and other.syllables_left == self.syllables_left

	def __hash__(self):
		return hash(str(self))