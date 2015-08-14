

def memoize(fn):
	known = dict()
	def new_fn(*args):
		key = tuple(args)
		if key not in known:
			known[key] = fn(*args)
		return known[key]
	return new_fn

class WordDB(object):

	def __init__(self):
		self.phonetic = self.load_phonetic_dict("/home/aryan/code/freestyle/db/cmudict-0.7b.txt") # { UPPER CASE WORD => [ LIST OF SOUNDS ]}
		self.word_pairs = self.load_2_grams("/home/aryan/code/freestyle/db/count_2w.txt") # { (WORD 1, WORD 2) => COUNT }
		self.rhyme_dict = self.create_rhyme_dict()
		self.prevs, self.nexts = self.create_prevs_and_nexts()

	def create_rhyme_dict(self):
		phonetic = self.phonetic

		ans = dict()

		for word in phonetic:
			last_syll = self.last_syllable(word)
			if last_syll not in ans:
				ans[last_syll] = list()
			ans[last_syll].append(word)
		return ans

	def create_prevs_and_nexts(self):
		word_pairs = self.word_pairs
		nexts = dict()
		prevs = dict()
		for (word1, word2) in word_pairs:
			count = word_pairs[(word1, word2)]
			if word1 not in nexts:
				nexts[word1] = list()
			if word2 not in prevs:
				prevs[word2] = list()
			nexts[word1].append( (word2, count) )
			prevs[word2].append( (word1, count) )
		return prevs, nexts

	def last_syllable(self, word):
		
		if word not in self.phonetic:
			return None

		sounds = self.phonetic[word]
		last_syll = 0
		for i in range(len(sounds)):
			sound = sounds[i]
			if sound[-1].isdigit():
				last_syll = i

		last_sounds = sounds[last_syll:]
		return tuple(last_sounds)

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
		return self.last_syllable(word1) == self.last_syllable(word2)

	def find_rhymes(self, words):
		if type(words) is str:
			words = [words]

		words = [a.upper() for a in words]

		word = words[0]
		last_syll = self.last_syllable(word)
		rhymes = self.rhyme_dict[last_syll]
		for word in words:
			if word not in rhymes:
				return list()
			rhymes.remove(word)

		return rhymes

	def find_next(self, word):
		word = word.upper()
		if word in self.nexts:
			return self.nexts[word]
		return list()

	def find_previous(self, word):
		word = word.upper()
		if word in self.prevs:
			return self.prevs[word]
		return list()

	def rhyme_sentence(self, words, max_syllables):
		
		ans = list()
		best_count = 0
		if type(words) is str:
			words = [words]
		rhymes = self.find_rhymes(words);
		print(rhymes)
		for rhyme in rhymes:
			chains = self.make_syllable_chain(rhyme, max_syllables, 0, "backwards")
			if not chains:
				continue
			for (count, words) in chains:
				if count > best_count:
					best_count = count
					yield words

	@memoize
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

		for (next_seed, curr_count) in nexts:

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
					weighted_count = chain_count / len(chain_words)**5

					if weighted_count >= best_count:
						best_count = weighted_count
						yield (chain_count, chain_words)

	def haiku(self, seed_word):
		l1_max = 5
		l2_max = 7
		l3_max = 5

		max_repeats = 4
		for (_ , l1_words) in self.make_syllable_chain(seed_word, l1_max, 0 ,  "backwards"):
			l1_reps = 0
			l1_lw = l1_words[-1]
			l1_lw_syllables = self.num_syllables(l1_lw)
			for l2_words in self.rhyme_sentence(l1_lw, l2_max):
				l1_reps += 1
				if l1_reps >= max_repeats:
					break;
				l2_reps = 0
				l2_words = l2_words[1:]
				l2_lw = l2_words[-1]
				for l3_words in self.rhyme_sentence([l2_lw], l3_max):
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

	


import cProfile, pstats, StringIO
pr = cProfile.Profile()
pr.enable()

word = "startup"
db = WordDB()
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

pr.disable()
s = StringIO.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print s.getvalue()
