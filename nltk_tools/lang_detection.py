from nltk import wordpunct_tokenize
from nltk.corpus import stopwords


def detect_langs(text):
	"""
	Uses the stopwords corpus in nltk to count the occurences of stopwords 
	in a given text and returns a dict of language and respective hits
	"""

	#Dict where results are stored
	lang_hits = {}

	#Tokenize the text and return only alphabet tokens
	tokens = wordpunct_tokenize(text)
	text_words = [word.lower() for word in tokens if word.isalpha()]

	#For all the stopwords available in NLTK
	#Count the overlapping words between provided text and stopword corpus
	#Store in dict
	for lang in stopwords.fileids():
		stop_words = stopwords.words(lang)
		intersect = [word for word in text_words if word in stop_words]
		lang_hits[lang] = len(intersect)

	return lang_hits
