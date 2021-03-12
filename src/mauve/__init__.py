from collections import defaultdict

import spacy

import gender_guesser.detector as gender
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import nltk
from mauve.wps import WPS

from mauve.models.synonym import Synonym
from mauve.nltk_load import load_nltk
from mauve.tagger import Tagger

load_nltk()


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
