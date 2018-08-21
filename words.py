import loader

phoneticDB = loader.PhoneticDictionary()
ngramDB = loader.NGramDB(edge_trim_ratio=0.5)

test_words = ["HELLO"]
for test_word in test_words:
	print(test_word, ",", phoneticDB.num_syllables[test_word])