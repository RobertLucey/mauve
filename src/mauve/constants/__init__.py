import os
import json
import string

import nltk
from nltk.corpus import words

from mauve.constants.profanity import (
    PROFANITY_LIST_RAW,
    PROFANITY_LIST,
    PROFANITY_SET,
    PROFANITY_WORDS
)
from mauve.constants.replacements import REPLACEMENTS
from mauve.constants.tokens import (
    TOKEN_MAP,
    SIMPLE_TOKEN_MAP,
    LIKELY_WORD_TOKENS
)


ENG_WORDS = set(nltk.corpus.words.words())
NLTK_ENG_WORDS = set(words.words())


ANALYSIS_VERSION = '7'
TOKEN_VERSION = '2'
BASE_DATA_PATH = '/opt/mauve/' if os.getenv('TEST_ENV', 'False') == 'False' else '/tmp/mauve'
GOODREADS_METADATA_PATH = os.path.join(BASE_DATA_PATH, 'metadata')
AUTHOR_METADATA_PATH = os.path.join(GOODREADS_METADATA_PATH, 'author_metadata.json')
TEXT_PATH = os.path.join(BASE_DATA_PATH, 'txt')
EPUB_PATH = os.path.join(BASE_DATA_PATH, 'epub')
CLEAN_EPUB_PATH = os.path.join(BASE_DATA_PATH, 'clean_books')
OIREACHTAS_DIR = os.path.join(BASE_DATA_PATH, 'oireachtas')
RAW_OIREACHTAS_DIR = os.path.join(BASE_DATA_PATH, 'raw_oireachtas')
TITLE_ID_MAP_PATH = os.path.join(GOODREADS_METADATA_PATH, 'title_id_map.json')


APOSTROPHES = {'’', '\''}
SENTENCE_TERMINATORS = {'.', '?', '!'}
SPEECH_QUOTES = {'`', '‘', '"', '``', '”', '“', '’'}
EXTENDED_PUNCTUATION = list(string.punctuation) + list(SPEECH_QUOTES)


LIKELY_PERSON_PREFIXES = {'dr', 'mr', 'ms', 'mrs', 'miss', 'sir'}

GENDER_PREFIXES = {
    'sir': 'male',
    'mr': 'male',
    'mister': 'male',
    'mr.': 'male',
    'lady': 'female',
    'miss': 'female',
    'ms.': 'female',
    'mrs.': 'female',
    'ms': 'female',
    'mrs': 'female'
}

PERSON_TITLE_PREFIXES = {
    'dr': 'Doctor'
}

PERSON_TRANSLATOR = str.maketrans('', '', ''.join(list('!"#$%&()*+,-/:;<=>?@[\\]^_`{|}~') + list(SPEECH_QUOTES)))
PERSON_PREFIXES = list(GENDER_PREFIXES.keys()) + list(PERSON_TITLE_PREFIXES.keys())
NOT_NAMES = {'I', 'My', 'An', 'don', 'Him', 'Her', 'So', 'Don', 'Said', 'Tut', 'Laughing', 'Little', 'Mystery', 'Christmas'}

SPEECH_WORDS = {'said', 'says', 'exclaimed', 'whispered', 'wrote', 'continued', 'told', 'shouted', 'called', 'recalled', 'explained', 'admitted', 'remarked', 'bellowed', 'shrieked', 'told', 'ask', 'asked', 'confided', 'fulminated', 'mused', 'rejoined', 'cried', 'panted', 'continued', 'ejaculated', 'replied', 'interrupted', 'remarked', 'declared', 'queried', 'repeated', 'added', 'lied', 'insisted', 'answered', 'returned', 'sighed', 'added', 'resumed', 'echoed', 'screamed', 'observed'}  # FIXME Need to include the ings, prob should use the stems
SPEAKERS = {'he', 'they', 'she', 'I', 'we', 'it', 'everyone', 'someone'}

ASSIGNMENT_WORDS = {'is', 'are', 'am', 'was', 'were', 'be', 'better not', 'should not', 'became'}

MALE_WORDS = {'himself', 'he', 'him', 'uncle', 'son', 'husband', 'dad', 'father', 'man', 'boy', 'lad', 'sir', 'gentleman', 'monsignor', 'fellow', 'fella', 'guy', 'bloke'}
EXTRA_MALE_NAMES = {'Chris', 'Éric', 'Bear', 'Ray', 'Dashiell', 'Vernor', 'Ishmael', 'Ayad', 'Dale', 'Etgar', 'Will'}
FEMALE_WORDS = {'herself', 'she', 'her', 'aunt', 'daughter', 'wife', 'mam', 'mother', 'woman', 'girl', 'lass', 'lady', 'madam', 'madame'}
EXTRA_FEMALE_NAMES = {'Mary', 'Kaylea', 'Isobelle', 'Kim', 'Luanne', 'Erin', 'Lauren', 'Connie', 'Glyn', 'Alyxandra', 'Carol', 'Kimberla', 'Lynsay', 'Rufi'}

BASE_LOUD_WORDS = {'loud', 'hard', 'bang', 'explode', 'shout', 'scream', 'shriek', 'yell', 'roar', 'screech', 'bellow', 'exclaim', 'howl', 'bark', 'heavy', 'yawp', 'blaring', 'blast', 'boom', 'deafen', 'piercing', 'thunderous', 'thunder', 'clatter', 'boom', 'squalk', 'clang', 'cacophony'}

LOUD_WORDS = list(BASE_LOUD_WORDS) + [w + 'ing' for w in BASE_LOUD_WORDS] + [w + 'ly' for w in BASE_LOUD_WORDS] + [w + 'ed' for w in BASE_LOUD_WORDS]

try:
    AUTHOR_METADATA = json.loads(open(AUTHOR_METADATA_PATH, 'r').read())
except FileNotFoundError:
    AUTHOR_METADATA = {}


BORING_WORDS = {'other', 'well', 'got', 'should', 'away', 'need', 'tell', 'here', 'cannot', 'never', 'now', 'just', 'through', 'think', 'too', 'see', 'want', 'much', 'still', 'head', 'hand', 'after', 'even', 'get', 'only', 'where', 'why', 'their', 'can', 'because', 'right', 'way', 'around', 'my', 'who', 'go', 'said', 'down', 'your', 'than', 'how', 'more', 'enough', 'going', 'off', 'then', 'before', 'over', 'by', 'time', 'or', 'am', 'them', 'an', 'there', 'this', 'will', 'know', 'one', 'me', 'like', 'back', 'when', 'into', 'been', 'so', 'about', 'were', 'are', 'from', 'no', 'we', 'did', 'all', 'him', 'if', 'up', 'what', 'do', 'could', 'be', 'would', 'at', 'but', 'out', 'dom', 'they', 'with', 'have', 'for', 'is', 'as', 'on', 'his', 'that', 'in', 'had', 'was', 'he', 'i', 'it', 'you', 'her', 'she', 'not', 'of', 'a', 'and', 'to', 'the', 'which', 'any', 'some', 'those', 'being', 'made', 'went', 'few', 'our', 'find', 'since', 'gone', 'came', 'again', 'us', 'own', 'may', 'its', 'such', 'both', 'ar', 'every', 'example', 'might', 'very', 'same', 'change', 'does', 'themselves', 'under', 'else', 'say', 'met', 'let', 'knew', 'ever', 'p', 'thou', 'come', 'put', 'thought', 'knew', 'make', 'give', 'once', 'felt', 'looking', 'always', 'behind', 'something', 'anyone', 'side', 'seen', 'm', 't', 'g', 'b', 'each', 'upon', 'another', 'really', 'these', 'though', 'above', 'told', 'c', 'y', 'en', 'el', 'also', 'de', 'la', 'un', 'las', 'many', 'most', 'se', 'lo', 'es', 'thing', 're', 'against', 'later', 'pol', 'wis', 'ae', 'esca', 'amma', 'soka', 'onto', 'toward', 'turned', 'perhaps', 'first', 'yet', 'although', 'ley', 'everyone', 'last', 'someone', 'between', 'far', 'set', 'maybe', 'look', 'day', 'days', 'must', 'cly', 's', 'whose', 'quite', 'trying', 'saw', 'chapter', 'lak', 'dis', 'dey', 'wid', 'j', 'anyway', 'rather', 'towards', 'instead', 'along', 'twenty', 'half', 'turn', 'year', 'four', 'bring', 'took', 'hour', 'minute', 'except', 'end', 'lot', 'saying', 'ten', 'given', 'try', 'standing', 'word', 'until', 'somehow', 'week', 'keep', 'close', 'able', 'across', 'six', 'least', 'call', 'h', 'continued', 'two', 'already', 'n', 'people', 'sort', 'while', 'three', 'next', 'anything', 'without', 'beside', 'hundred', 'thousand', 'dor', 'sen', 'dak', 'amba', 'forward', 'watched', 'name', 'q', 'o', 'says', 'asked', 'dp'}
