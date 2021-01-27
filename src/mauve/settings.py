import os

REMOVE_STOPWORDS = eval(os.getenv('REMOVE_STOPWORDS', 'False'))
WORDNET_REPLACE = eval(os.getenv('WORDNET_REPLACE', 'False'))
