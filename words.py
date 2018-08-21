import loader
import graph

phoneticDB = loader.PhoneticDB()
ngramDB = loader.NGramDB(edge_trim_ratio=0.8)

## General Info
print("There are {} words in the phonetic dictionary".format(len(phoneticDB.phones.keys())))
print("There are {} rhyme endings in the phonetic dictionary".format(len(phoneticDB.rhyme_index.keys())))
print("There are {} 2-gram pairs".format(len(ngramDB.word_pairs.keys())))

## Do some manual inspection with test words
test_words = ["HELLO", "ANDY", "HOWDY", "FRIEND", "THANK", "EVERLASTING"]
# test_words = []
for test_word in test_words:
	print("\n###")
	print(test_word)
	print("Rhyme sound", phoneticDB.extract_rhyme(test_word))
	print("Sum Syllables", phoneticDB.num_syllables[test_word])
	rhymes = phoneticDB.find_rhymes(test_word) 
	print("5 Rhymes", rhymes[:min(5, len(rhymes))])
	nexts = ngramDB.find_next(test_word) 
	print("5 Nexts", nexts[:min(5, len(nexts))])


SAVE_FREQ = 1000
def test_graph(num_syllables, rhyme_word, max_poems):
	word_graph = graph.TargetedGraph(phoneticDB, ngramDB, num_syllables, rhyme_word)

	with open("examples/targeted_{}_{}_{}.txt".format(rhyme_word, num_syllables, max_poems), "w") as fp:
		poems = []
		for word_list in word_graph.populate_graph():
			poem = " ".join(word_list).lower()
			poems.append(poem)
			if len(poems) % SAVE_FREQ == 0:
				print("Saving Poems")
				fp.write("\n".join(poems))
			if len(poems) > max_poems:
				return
		fp.write("\n".join(poems))
	## General Graph Info
	print("There are {} vertices in the word graph".format(len(word_graph.vertices)))

# TODO: Not the most effecient order to loop
# test_graph(5, "FRIEND", 100)
# for max_poems in (50000, 500000, 5000000):
# 	for rhyme_word in test_words:
# 		for num_syllables in (3, 5, 7):
# 			test_graph(num_syllables, rhyme_word, max_poems)
