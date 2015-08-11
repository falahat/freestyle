

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

	def rhymes(self, word1, word2):
		if word1 == word2:
			return False
		w1_sounds = self.phonetic[word1]
		w2_sounds = self.phonetic[word2]

		w1_last_syll = 0
		for i in range(len(w1_sounds)):
			w1_sound = w1_sounds[i]
			if w1_sound[-1].isdigit():
				w1_last_syll = i

		w1_last_sounds = w1_sounds[w1_last_syll:]

		if len(w2_sounds) < len(w1_last_sounds):
			return False

		for i in range(len(w1_last_sounds)):
			offset = len(w2_sounds) - len(w1_last_sounds)
			w2_index = i + offset
			if w2_sounds[w2_index] != w1_last_sounds[i]:
				return False
		return True

	def find_rhymes(self, word):
		word = word.upper()

		def filter_fn(other_word):
			return self.rhymes(word, other_word)

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
		ans = list()
		best_count = 0
		for rhyme in rhymes:
			chains = self.make_syllable_chain(rhyme, max_syllables, 0, "backwards")
			if not chains:
				continue
			for (count, words) in chains:
				if count > best_count:
					best_count = count
					yield words


	def num_syllables(self, word):
		# TODO: very janky currently
		ans = 0
		if word in self.phonetic:
			sounds = self.phonetic[word]
			for sound in sounds:
				if sound[-1].isdigit():
					ans += 1
		return ans

	def make_syllable_chain(self, seed_word, max_syllables=5, best_count=0, direction="forward"):
		old_best_count = best_count
		seed_word = seed_word.upper()
		curr_syllables = self.num_syllables(seed_word)
		if curr_syllables == 0:
			return
		new_syllables = max_syllables - curr_syllables
		if new_syllables == 0:
			yield (0, [seed_word])
		if new_syllables < 0:
			return

		if direction == "forward":
			nexts = self.find_next(seed_word)
		else:
			nexts = self.find_previous(seed_word)

		max_index = min(len(nexts)-1, 5)
		nexts = {nexts.keys()[i] : nexts[nexts.keys()[i]] for i in range(max_index)}
		for (word1, word2) in nexts.keys():
			curr_count = nexts[(word1, word2)]

			if direction == "forward":
				next_seed = word2
			else:
				next_seed = word1

			chains = self.make_syllable_chain(next_seed, new_syllables, old_best_count, direction)

			if chains:
				for chain in chains:

					chain_count = chain[0]
					chain_words = chain[1]


					if direction == "forward":
						chain_words.insert(0, seed_word)
					else:
						chain_words.insert(len(chain_words), seed_word)
					chain_count += curr_count

					if chain_count >= best_count:
						best_count = chain_count
						yield (chain_count, chain_words)

	def haiku(self, seed_word):
		l1_max = 5
		l2_max = 7
		l3_max = 5

		max_repeats = 5
		for (_ , l1_words) in self.make_syllable_chain(seed_word, l1_max, 0 ,  "backwards"):
			l1_reps = 0
			l1_lw = l1_words[-1]
			l1_lw_syllables = self.num_syllables(l1_lw)
			l2_chain = self.make_syllable_chain(l1_lw, l2_max + l1_lw_syllables, 0, "forward")
			if not l2_chain:
				continue
			for (_ , l2_words) in l2_chain:
				l1_reps += 1
				if l1_reps >= max_repeats:
					break;
				l2_reps = 0
				l2_words = l2_words[1:]
				l2_lw = l2_words[-1]
				for l3_words in self.rhyme_sentence(l1_lw, l3_max):
					l2_reps += 1
					if l2_reps >= max_repeats:
						break;

					l3_lw = l3_words[-1]
					l1 = " ".join(l1_words)
					l2 = " ".join(l2_words)
					l3 = " ".join(l3_words)
					header = "A Robot Haiku :) "
					ans = "\\\\ {} \n\t{} \n\t{} \n\t{}".format(header, l1, l2, l3)
					config = "l1_lw: {}".format(l1_lw)
					yield ans

	

db = WordDB()
word = "Harmony"
rhymes = db.find_rhymes(word)
nexts = db.find_next(word)
prevs = db.find_previous(word)

haikus = db.haiku(word)

i=0
max_i = 100
buff = "***"
for haiku in haikus:
	i += 1
	print(buff*20)
	print("POEM # {} # POEM".format(i))
	print(haiku)
	if i == max_i:
		break;