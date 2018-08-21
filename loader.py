CMU_DICTIONARY_PATH = "./db/cmudict-0.7b.txt"
CMU_PHONES_PATH = "./db/cmudict-0.7b.phones.txt"
TWO_GRAM_PATH = "./db/count_2w.txt"
ACCEPT_NEAR_RHYME = True

class PhoneticDB(object):
	def __init__(self, dict_path=CMU_DICTIONARY_PATH, phones_path=CMU_PHONES_PATH, load_instantly=True):
		self.dict_path = dict_path;
		self.phones_path = phones_path

		self.phone_types = None  # { phone => phone type (i.e. vowel, fricative)}
		self.phones = None # { word => [ list of phones for the word ]}
		self.num_syllables = None # { word => integer num syllables}
		self.rhyme_index = None  # {(phones comprising last syllable) => [list of words]}
		
		if load_instantly:
			self.load()

	def load(self):
		# TODO: Convert this to some kind of streaming to avoid the duplicate code?
		self.phones = self.load_phonetic_dict(self.dict_path) 
		self.phone_types = self.load_phones_description(self.phones_path)
		self.rhyme_index = self.create_rhyme_index();
		self.num_syllables = self.create_num_syllables();


	### Load Files

	def load_phonetic_dict(self, path):
		result = dict()
		with open(path) as fp:
			for line in fp:
				if not (len(line) > 0 and line[0].isalnum()):
					continue # Ignore Punctuation and Numbers
				phones = line.upper().split()
				word = phones.pop(0)
				if ACCEPT_NEAR_RHYME: # Trim off the number, we don't care about that level of precision
					phones = map(lambda phone: phone[:-1] if phone[-1].isdigit() else phone, phones)
				result[word] = phones
		return result

	def load_phones_description(self, path):
		result = dict()
		with open(path) as fp:
			for line in fp:
				# TODO: Will throw if the line doesn't split into 2
				phone, phone_type = line.upper().split()
				result[phone] = phone_type
		return result


	### Create Useful Databases

	def create_num_syllables(self):
		result = dict()
		for word in self.phones:
			num_syllables = self.extract_num_syllables(word)
			result[word] = num_syllables
		return result

	def create_rhyme_index(self):
		result = dict()
		for word in self.phones:
			rhyme = self.extract_rhyme(word)
			if rhyme not in result:
				result[rhyme] = list() # TODO: maybe set?
			result[rhyme].append(word)
		return result

	### Single Word-Level Extractors

	def extract_rhyme(self, word):
		if word not in self.phones:
			return None
		phones = self.phones[word]
		last_vowel_idx = -1; # Beginning of the last vowel segment
		is_vowel = [self.phone_types[phone] == "VOWEL" for phone in phones]
		
		is_start_of_vowel_segment = [is_vowel[0]] 
		is_start_of_vowel_segment += [(is_vowel[i] and not is_vowel[i - 1]) for i in range(1, len(is_vowel))]
		for i in range(len(is_start_of_vowel_segment)):
			last_vowel_idx = i if is_start_of_vowel_segment[i] else last_vowel_idx

		last_sounds = phones[last_vowel_idx:]
		return tuple(last_sounds)

	def extract_num_syllables(self, word):
		if word not in self.phones:
			return None

		phones = self.phones[word]
		is_vowel = [self.phone_types[phone] == "VOWEL" for phone in phones]
		
		is_start_of_vowel_segment = [is_vowel[0]] 
		is_start_of_vowel_segment += [(is_vowel[i] and not is_vowel[i - 1]) for i in range(1, len(is_vowel))]
		num_syllables = sum([1 if el else 0 for el in is_start_of_vowel_segment])
		# We define the number of syllables as the number of contiguous groups of vowels uninterrupted by a non-vowel sound. 
		return num_syllables

	### Util Methods

	def rhymes(self, word1, word2):
		if word1 == word2: # Because it's cheating
			return False
		return self.extract_rhyme(word1) == self.extract_rhyme(word2)

	def find_rhymes(self, word):
		word = word.upper()
		rhyme_syll = self.extract_rhyme(word)
		rhymes = self.rhyme_index[rhyme_syll]
		return rhymes


class NGramDB(object):
	def __init__(self, two_gram_path=TWO_GRAM_PATH, edge_trim_ratio=0, load_instantly=True):
		self.two_gram_path = two_gram_path
		self.edge_trim_ratio = edge_trim_ratio

		self.word_pairs = None
		self.prevs, self.nexts = None, None
		if load_instantly:
			self.load()

	def load(self):
		self.word_pairs = self.load_2_grams(self.two_gram_path) # { (WORD 1, WORD 2) => COUNT }
		self.prevs, self.nexts = self.create_prevs_and_nexts()

	def create_prevs_and_nexts(self):
		nexts = dict()
		prevs = dict()
		for (word1, word2) in self.word_pairs:
			count = self.word_pairs[(word1, word2)]
			if word1 not in nexts:
				nexts[word1] = list()
			if word2 not in prevs:
				prevs[word2] = list()
			nexts[word1].append( (word2, count) )
			prevs[word2].append( (word1, count) )
		return prevs, nexts

	def load_2_grams(self, path):
		result = dict()
		total = 0
		counts = dict()

		# Load the file
		with open(path) as fp:
			for line in fp:
				entries = line.upper().split()
				if len(entries) == 3:
					word1, word2, count = entries
					count = int(count)
					if (word1, word2) not in counts:
						counts[(word1, word2)] = 0
					counts[(word1, word2)] += count
					total += count

		# Compute percentage and trim edges
		total = float(total)
		counts =  sorted(counts.items(), key=lambda (w1w2, count): count)
		trim_idx = (1-self.edge_trim_ratio)*len(counts) # Trim the last ratio*(total rows) rows
		counts = counts[:int(trim_idx)] 
		for word1_word2, count in counts:
			result[word1_word2] = count / total
		return result

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
	
