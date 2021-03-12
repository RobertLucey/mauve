from collections import defaultdict

import spacy

import gender_guesser.detector as gender
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import nltk
from mauve.wps import WPS

from mauve.models.synonym import Synonym
from mauve.nltk_load import load_nltk
from mauve.tagger import Tagger

try:
    nltk.data.find('corpora/words')
except LookupError:  # pragma: nocover
    nltk.download('words')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:  # pragma: nocover
    nltk.download('wordnet')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:  # pragma: nocover
    nltk.download('punkt')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:  # pragma: nocover
    nltk.download('averaged_perceptron_tagger')


GENDER_DETECTOR = gender.Detector()
VADER = SentimentIntensityAnalyzer()
try:
    ENCORE = spacy.load('en_core_web_sm')
except:  # pragma: nocover
    from spacy.cli import download
    download('en')
    ENCORE = spacy.load('en_core_web_sm')

try:
    ENCORE_LG = spacy.load('en_core_web_lg')
except:  # pragma: nocover
    from spacy.cli import download
    download('en_core_web_lg')
    ENCORE_LG = spacy.load('en_core_web_lg')


WPS = WPS(print_rate=10000)
SYNONYM = Synonym()
