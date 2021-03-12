from collections import defaultdict
import random

import spacy

import gender_guesser.detector as gender
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import nltk
from mauve.wps import WPS

from mauve.models.synonym import Synonym

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

from nltk.tag.perceptron import PerceptronTagger


TAGGER = PerceptronTagger()


class Tagger():

    def pos_tag(self, tokens):
        if tokens == ['']:
            return []

        tagged_tokens = TAGGER.tag(tokens)

        if random.random() < 0.5:
            count = 0
            for tok, tag in tagged_tokens:
                if count % 2 == 0:
                    TAGGER.tagdict[tok] = tag

        return tagged_tokens
