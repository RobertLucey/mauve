import random
from collections import defaultdict

import spacy

import gender_guesser.detector as gender
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import nltk
try:
    from nltk.tag.perceptron import PerceptronTagger
except:
    nltk.download('averaged_perceptron_tagger')
    from nltk.tag.perceptron import PerceptronTagger

from mauve.wps import WPS

from mauve.models.synonym import Synonym


GENDER_DETECTOR = gender.Detector()
VADER = SentimentIntensityAnalyzer()
TAGGER = PerceptronTagger()
try:
    ENCORE = spacy.load('en_core_web_sm')
except:  # pragma: nocover
    from spacy.cli import download
    download('en')
    ENCORE = spacy.load('en_core_web_sm')
WPS = WPS(print_rate=10000)
SYNONYM = Synonym()

ALL = defaultdict(int)


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


