# -*- coding: utf-8 -*-
# Environment: Python 3.5
# Author: Sathyan Murugan

"""
This file contains methods to n-gramize strings that may also have numerical data attributions
As an example, this script can be used to n-gramize search terms (on google for instance)
and group each distinct n-gram by attributes such as visits, clicks, conversions etc

"""

import pandas as pd
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.util import ngrams
from nltk.stem.snowball import SnowballStemmer
import string


#Inputs
stop = stopwords.words('english')
stemmer = SnowballStemmer('english')
n = 1 # number of n-grams desired

# Sample data. As many numerical columns such as votes can be added as desired. 
statements = ['cats are awesome', 'dogs are 20 times more awesome','both cats and dogs are awesome']
votes = [5,3,2]
df = pd.DataFrame({
	'statements':statements,
	'votes':votes})

# Convert statements into word tokens
df['statements'] = df['statements'].apply(lambda row: word_tokenize(row))

#Convert words into their word stems if necessary (House => Hous, Cats => Cat)
df['statements'] = df['statements'].apply(lambda row: [stemmer.stem(item) for item in row])

# Remove unnecessary words/numbers/symbols
df['statements'] = df['statements'].apply(lambda row: [item for item in row 
                                              		if item.lower() not in stop
                                              		and item not in item.strip(string.ascii_letters)])

# Convert the tokens back to a string
df['statements'] = df['statements'].apply(lambda row: ' '.join(item for item in row))

# Add column to the dataframe that contains the search statements split into sorted ngrams
df['tokens'] = df['statements'].apply(lambda row: list(sorted(ngrams(row.split(),n))))

# This column now needs to be stacked vertically. For more info, read here:
# http://stackoverflow.com/questions/17116814/pandas-how-do-i-split-text-in-a-column-into-multiple-rows
s = df['tokens'].apply(pd.Series,1).stack()
s.index = s.index.droplevel(-1) # to line up with df's index
s.name = 'ngrams' # needs a name to join

# Remove old tokens, statements column
del df['tokens']
del df['statements']

# Add the new column to the Dataframe
df = df.join(s)

# Group by the ngrams
df = df.groupby(df['ngrams']).sum()

#Sort the data if necessary
df = df.sort_values(df.columns[0], ascending = False)
