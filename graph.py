
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
		return node.word in self.phonetic_db.phones and node.syllables_left >= 0;

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
		children = self.children(node1)
		word2 = node2.word
		for word, count in children:
			if word == word2:
				return 1 - count
		return MAX_DISTANCE
	
	def search_nodes(self, desired_word=None, desired_rhyme=None, desired_syllables_left=None):
		# TODO: effeciently query the nodes. Possibly generate on demand?
		pass;

class RhymeTargetedGraph(WordGraph):
	def __init__(self, phonetic_db, ngram_db, root_node, rhyme_word):
		super(RhymeTargetedGraph, self).__init__(phonetic_db, ngram_db, root_node)
		self.rhyme_word = rhyme_word
	
	def is_node_valid(self, node):
		if super(RhymeTargetedGraph, self).is_node_valid(node):
			if node.syllables_left == 0:
				return self.phonetic_db.rhymes(self.rhyme_word, node.word)
		return True

class WordNode(object):
	def __init__(self, word, syllables_left):
		self.word = word
		self.syllables_left = syllables_left

	def __str__(self):
		return "({}, {})".format(self.word, self.syllables_left)