import logging
import random

import gender_guesser.detector as gender
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import spacy

import nltk
from nltk.tag.perceptron import PerceptronTagger

from mauve.wps import WPS
from mauve.models.synonym import Synonym


formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger('mauve')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def load_nltk():
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


def load_spacy():
    try:
        ENCORE = spacy.load('en_core_web_sm')
    except:  # pragma: nocover
        from spacy.cli import download
        download('en')

    try:
        ENCORE_LG = spacy.load('en_core_web_lg')
    except:  # pragma: nocover
        from spacy.cli import download
        download('en_core_web_lg')


load_nltk()
load_spacy()


GENDER_DETECTOR = gender.Detector()
VADER = SentimentIntensityAnalyzer()

ENCORE = spacy.load('en_core_web_sm')
ENCORE.max_length = 2_000_000

ENCORE_LG = spacy.load('en_core_web_lg')
ENCORE_LG.max_length = 2_000_000

WPS = WPS(print_rate=10000)
SYNONYM = Synonym()

TAGGER = PerceptronTagger()


class Tagger():
    """
    A pos_tag tagger that caches a fair bit

    Is tagger contextual? If not this isn't safe... TODO test
    """

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
