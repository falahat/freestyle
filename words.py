import loader
import graph

phoneticDB = loader.PhoneticDB()
ngramDB = loader.NGramDB(edge_trim_ratio=0.5)

## General Info
print("There are {} words in the phonetic dictionary".format(len(phoneticDB.phones.keys())))
print("There are {} rhyme endings in the phonetic dictionary".format(len(phoneticDB.rhyme_index.keys())))
print("There are {} 2-gram pairs".format(len(ngramDB.word_pairs.keys())))

## Do some manual inspection with test words
test_words = ["HELLO", "HOWDY", "FRIEND", "THANK", "EVERLASTING"]
test_words = []
for test_word in test_words:
	print("\n###")
	print(test_word)
	print("Sum Syllables", phoneticDB.num_syllables[test_word])
	rhymes = phoneticDB.find_rhymes(test_word) 
	print("5 Rhymes", rhymes[:min(5, len(rhymes))])
	nexts = ngramDB.find_next(test_word) 
	print("5 Nexts", nexts[:min(5, len(nexts))])

# Let's create a sentence w/ 5 syllables that rhymes with "Friend"
NUM_SYLLABLES = 5
RHYME_WORD = "FRIEND"

word_graph = graph.WordGraph(phoneticDB, ngramDB)