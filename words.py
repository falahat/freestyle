import loader
import graph

phoneticDB = loader.PhoneticDB()
ngramDB = loader.NGramDB(edge_trim_ratio=0.9)

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

START_WORD = "HELLO"
NUM_SYLLABLES = 5
RHYME_WORD = "MAY"
DESTINATION_NODES = set([graph.WordNode(word, 0) for word in phoneticDB.find_rhymes(RHYME_WORD)])
print(DESTINATION_NODES)
START_NODES = [graph.WordNode(START_WORD, NUM_SYLLABLES)]
word_graph = graph.TargetedGraph(phoneticDB, ngramDB, START_NODES, DESTINATION_NODES)
word_graph.populate_graph()

## General Graph Info
print("There are {} vertices in the word graph".format(len(word_graph.vertices)))
