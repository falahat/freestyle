import loader

phoneticDB = loader.PhoneticDictionary()
ngramDB = loader.NGramDB()

test_words = ["HELLO"]
for test_word in test_words:
	print(phoneticDB.num_syllables[test_word])