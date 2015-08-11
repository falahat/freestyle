

class WordDB(object):

	def __init__(self):
		self.phonetic = self.load_phonetic_dict("/home/aryan/code/freestyle/db/cmudict-0.7b.txt") # { UPPER CASE WORD => [ LIST OF SOUNDS ]}
		self.word_pairs = self.load_2_grams("/home/aryan/code/freestyle/db/count_2w.txt") # { (WORD 1, WORD 2) => COUNT }

	def load_2_grams(self, path):
		ans = dict()
		with open(path) as fp:
			for line in fp:
				entries = line.upper().split()
				if len(entries) == 3:
					word1, word2, count = entries
					count = int(count)
					if (word1, word2) not in ans:
						ans[(word1, word2)] = 0
					ans[(word1, word2)] += count
		return ans

	def load_phonetic_dict(self, path):
		ans = dict()
		with open(path) as fp:
			for line in fp:
				line = line.upper()
				if len(line) > 0 and line[0].isalnum():
					sounds = line.split()
					word = sounds.pop(0)
					ans[word] = sounds
		return ans

	def find_rhymes(self, word):
		word = word.upper()
		word_sounds = self.phonetic[word]

		def filter_fn(other_word):
			other_sounds = self.phonetic[other_word]
			return other_sounds[-1] == word_sounds[-1] and other_word != word

		ans = filter(filter_fn, self.phonetic.keys())
		return ans

	def find_next(self, word):
		word = word.upper()
		def filter_fn( (word1, word2) ):
			return word1 == word
		all_pairs = self.word_pairs
		new_keys = filter(filter_fn, all_pairs.keys())
		new_pairs = { k : all_pairs[k] for k in new_keys}
		return new_pairs

	def find_previous(self, word):
		word = word.upper()
		def filter_fn( (word1, word2) ):
			return word2 == word
		all_pairs = self.word_pairs
		new_keys = filter(filter_fn, all_pairs.keys())
		new_pairs = { k : all_pairs[k] for k in new_keys}
		return new_pairs

	def rhyme_sentence(self, word, max_syllables):
		rhymes = self.find_rhymes(word);
		max_i = min(len(rhymes) - 1, 5)
		rhymes = rhymes[:max_i];
		ans = list()
		for rhyme in rhymes:
			chains = self.make_syllable_chain(rhyme, max_syllables, "backwards")
			if not chains:
				continue
			max_i = min(len(chains) - 1, 5)
			chains = sorted(chains, key=lambda (count, words): count)[:max_i]
			for (count, words) in chains:
				ans.append(words)
		return ans

	def num_syllables(self, word):
		# TODO: very janky currently
		ans = 0
		if word in self.phonetic:
			sounds = self.phonetic[word]
			for sound in sounds:
				if sound[-1].isdigit():
					ans += 1
		return ans

	def make_syllable_chain(self, seed_word, max_syllables=5, direction="forward"):
		seed_word = seed_word.upper()
		curr_syllables = self.num_syllables(seed_word)
		if curr_syllables == 0:
			return False
		new_syllables = max_syllables - curr_syllables
		if new_syllables == 0:
			return [(0, [seed_word])]
		if new_syllables < 0:
			return False

		if direction == "forward":
			nexts = self.find_next(seed_word)
		else:
			nexts = self.find_previous(seed_word)

		max_index = min(len(nexts)-1, 5)
		nexts = {nexts.keys()[i] : nexts[nexts.keys()[i]] for i in range(max_index)}
		ans = list()
		for (word1, word2) in nexts.keys():
			curr_count = nexts[(word1, word2)]

			if direction == "forward":
				next_seed = word2
			else:
				next_seed = word1

			chains = self.make_syllable_chain(next_seed, new_syllables, direction)

			if chains and len(chains) > 0:
				for (chain_count, chain_words) in chains:

					if direction == "forward":
						chain_words.insert(0, seed_word)
					else:
						chain_words.insert(len(chain_words), seed_word)
					chain_count += curr_count
					ans.append( (chain_count, chain_words) )
		if len(ans) == 0:
			return False
		else:
			ans = sorted(ans, key=lambda (chain_count, words): chain_count)
			return ans

	def haiku(self, seed_word):
		l1_max = 5
		l2_max = 7
		l3_max = 5
		for (_ , l1_words) in self.make_syllable_chain(seed_word, l1_max, "forward"):
			l1_lw = l1_words[-1]
			for l2_words in self.rhyme_sentence(l1_lw, l2_max):
				l2_lw = l2_words[-1]
				for l3_words in self.rhyme_sentence(l2_lw, l3_max):
					l3_lw = l3_words[-1]
					l1 = " ".join(l1_words)
					l2 = " ".join(l2_words)
					l3 = " ".join(l3_words)
					header = "A Robot Haiku :) "
					ans = "{} \n {} \n {} \n {}".format(header, l1, l2, l3)
					yield ans

	

db = WordDB()
word = "hello"
rhymes = db.find_rhymes(word)
nexts = db.find_next(word)
prevs = db.find_previous(word)

for haiku in db.haiku(word):
	print(haiku)
	print("****"*20)