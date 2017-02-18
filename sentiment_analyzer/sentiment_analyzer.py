import warnings
from email_reply_parser import EmailReplyParser
# Silence warnings about missing twython library which is not needed here
with warnings.catch_warnings():
	warnings.simplefilter("ignore", UserWarning)
	from nltk.sentiment.vader import SentimentIntensityAnalyzer
	from nltk import tokenize,wordpunct_tokenize
	from nltk.corpus import stopwords
from datetime import date, timedelta
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def parse_sender_name(sender_name):
	"""
	Attempts to extract names from the email sender name
	"""

	#If there is no sender_name available, end the function
	if sender_name == None or sender_name == '':
		return
	
	#if sender_name like email address
	if '@' in sender_name:
		username = sender_name.split('@')[0]
		dirty_names = wordpunct_tokenize(username)
		clean_names = [name for name in dirty_names 
						if name.isalpha()
						and len(name) > 1]
	else:
		dirty_names = wordpunct_tokenize(sender_name)
		clean_names = [name for name in dirty_names 
						if name.isalpha()
						and len(name) > 1]

	return clean_names



def parse_email(email_thread,sender_names=None):
	"""
	Attempts to extract the actual content of an email, by
	1. removing any threads and extracting the most recent email
	2. truncating the email at the first available "truncator"
    """


	if not email_thread:
		return

	#Parse email and extract most recent reply, ignore any threads
	#https://github.com/zapier/email-reply-parser
	email = EmailReplyParser.parse_reply(email_thread)

	#Define parameters to further truncate the email

	signoffs = ['kind regards','kindest regards','best regards','br','regards','rgds',
	'thank you','thank you very much','many thanks','thanks','thx','tks','txs','thanks again',
	'yours truly','yours sincerely','yours faithfully','sincerely','faithfully',
	'best','wishes','take care','looking forward', 'cheers',]

	footers = ['sent from my','sent via','from:','to stop receiving these']

	#Attempt to truncate the email by one of the different 'truncators'
	#and return value after the first "truncation"
	#Intentionally ordered as signoffs, names, footers (the structure of an email)


	for sign_off in signoffs:
		if sign_off + ',\n' in email.lower():
			truncated_email = email[0:email.lower().find(sign_off + ',\n')]
			return truncated_email

		if sign_off + ', \n' in email.lower():
			truncated_email = email[0:email.lower().find(sign_off + ', \n')]
			return truncated_email

		if sign_off + '\n'  in email.lower():
			truncated_email = email[0:email.lower().find(sign_off + '\n')]
			return truncated_email

		if sign_off + ' \n'  in email.lower():
			truncated_email = email[0:email.lower().find(sign_off + ' \n')]
			return truncated_email

	if sender_names:

		for name in sender_names:
			if name.lower() in email.lower():
				truncated_email = email[0:email.lower().find(name.lower())]
				return truncated_email


	for footer in footers:
		if footer in email.lower():
			truncated_email = email[0:email.lower().find(footer)]
			return truncated_email


	return email


def detect_langs(text):
	"""
	Uses the stopwords corpus in nltk to count the occurences of stopwords 
	in a given text and returns a dict of language and respective hits
	"""
	if not text:
		return
	
	lang_hits = {}
	tokens = wordpunct_tokenize(text)
	text_words = [word.lower() for word in tokens if word.isalpha()]

	for lang in stopwords.fileids():
		stop_words = stopwords.words(lang)
		intersect = [word for word in text_words if word in stop_words]

		lang_hits[lang] = len(intersect)

	return lang_hits



def sentiment(text,min_word_count=None,string_break_type=None):
	"""
	Using the sentiment analyzer in the nltk library, 
	return the compound sentiment score for a given piece of text
	
	- if string_break_type == None: analyze text as whole as return score
	
	- if string_break_type = ='l': break text by new line and analyze each line
	- if string_break_type = ='s': break text by sentence and analyze each sentence
	- if string_break_type = ='ls': break text by line and sentence, and analyze each phrase
	- Average the resulting scores and return the average score 
	
	- Conditions for a line/sentence to be included in the l/s/ls analysis:
	1. min_word_count must be satisfied
	2. - 0.1 <= sentiment_score >= 0.1

	"""

	#Initialize analyzer class from nltk
	analyzer = SentimentIntensityAnalyzer()

	#If no string_break_type is specified 
	if string_break_type == None:
		return analyzer.polarity_scores(text)['compound']

	total_sentiment_score = 0.0
	counter = 0.0


	if string_break_type == 'ls':
		line_list = tokenize.LineTokenizer(blanklines='discard').tokenize(text)
		sentence_list = [tokenize.sent_tokenize(line) for line in line_list]

		#Flatten the list
		strings = [val for sublist in sentence_list for val in sublist]
	
	elif string_break_type == 'l':
		strings = tokenize.LineTokenizer(blanklines='discard').tokenize(text)
	
	elif string_break_type == 's':
		strings = tokenize.sent_tokenize(text)

	for string in strings:
		words_raw = wordpunct_tokenize(string)
		words = [word for word in words_raw if word.isalpha()]

		#if not min_word_count, goto next
		if len(words) < min_word_count:
			continue

		vs = analyzer.polarity_scores(string)
		sentiment_score = vs['compound']

		#if score is between -0.1 and 0.1, goto next
		if sentiment_score > -0.1 and sentiment_score < 0.1:
			continue
		
		counter += 1
		total_sentiment_score += sentiment_score

	if total_sentiment_score == 0.0:
		return total_sentiment_score
	else:	
		return round(total_sentiment_score/counter,4)



def get_sentiment(text,min_word_count=1):
	"""
	- Use sentiment() to generate sentiment scores for each analysis type
	- While the minimum score from all methods is less than 0.5
	(excluding 0.0 scores which means sentiment couldnt be generated)
			
			- return min score
			- else return max score 
	
	"""

	line_sentiment = sentiment(text,min_word_count,"l")
	sentence_sentiment = sentiment(text,min_word_count,"s")
	line_sentence_sentiment = sentiment(text,min_word_count,'ls')
	full_sentiment = sentiment(text)

	min_score = min(line_sentiment,sentence_sentiment,line_sentence_sentiment,full_sentiment)
	max_score = max(line_sentiment,sentence_sentiment,line_sentence_sentiment,full_sentiment)

	if round(min_score,1) < 0.5 and min_score!= 0.0:
		return min_score
	else:
		return max_score


if __name__ =='__main__':

	text = """

	 """

	score = get_sentiment(text)

	print (score)