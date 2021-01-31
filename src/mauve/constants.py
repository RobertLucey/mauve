import os

from mauve.profanity import PROFANITY_LIST
from mauve.names import NAMES

import nltk


ENG_WORDS = set(nltk.corpus.words.words())

LIKELY_WORD_TOKENS = [
    #'(',
    #')',
    #'``',
    #',',
    #"''",
    #'.',
    #'#',
    #'$',
    #':',
    #'SYM',
    'CC',
    #'CD',
    'DT',
    'EX',
    'FW',
    'IN',
    'JJ',
    'JJR',
    'JJS',
    'LS',
    'MD',
    'NN',
    'NNS',
    'NNP',
    'NNPS',
    'PDT',
    'POS',
    'PRP',
    'PRP$',
    'RB',
    'RBR',
    'RBS',
    'RP',
    'TO',
    'UH',
    'VB',
    'VBD',
    'VBG',
    'VBN',
    'VBP',
    'VBZ',
    'WDT',
    'WP',
    'WP$',
    'WRB',
]

TOKEN_MAP = {
    '(': 'open parenthesis',
    ')': 'close parenthesis',
    '``': 'open quote',
    ',': 'comma',
    "''": 'close quote',
    '.': 'period',
    '#': 'pound sign (currency marker)',
    '$': 'dollar sign (currency marker)',
    ':': 'colon',
    'SYM': 'Symbol (mathematical or scientific)',
    'CC': 'coordinating conjunction',
    'CD': 'cardinal digit',
    'DT': 'determiner',
    'EX': 'existential there (like: \'there is\' ... think of it like \'there exists\')',
    'FW': 'foreign word',
    'IN': 'preposition/subordinating conjunction',
    'JJ': 'adjective \'big\'',
    'JJR': 'adjective, comparative \'bigger\'',
    'JJS': 'adjective, superlative \'biggest\'',
    'LS': 'list marker 1)',
    'MD': 'modal could, will',
    'NN': 'noun, singular \'desk\'',
    'NNS': 'noun plural \'desks\'',
    'NNP': 'proper noun, singular \'Harrison\'',
    'NNPS': 'proper noun, plural \'Americans\'',
    'PDT': 'predeterminer \'all the kids\'',
    'POS': 'possessive ending parent\'s',
    'PRP': 'personal pronoun I, he, she',
    'PRP$': 'possessive pronoun my, his, hers',
    'RB': 'adverb very, silently,',
    'RBR': 'adverb, comparative better',
    'RBS': 'adverb, superlative best',
    'RP': 'particle give up',
    'TO': 'to go \'to\' the store.',
    'UH': 'interjection, errrrrrrrm',
    'VB': 'verb, base form take',
    'VBD': 'verb, past tense took',
    'VBG': 'verb, gerund/present participle taking',
    'VBN': 'verb, past participle taken',
    'VBP': 'verb, sing. present, non-3d take',
    'VBZ': 'verb, 3rd person sing. present takes',
    'WDT': 'wh-determiner which',
    'WP': 'wh-pronoun who, what',
    'WP$': 'possessive wh-pronoun whose',
    'WRB': 'wh-abverb where, when'
}

SIMPLE_TOKEN_MAP = {
    '(': 'open parenthesis',
    ')': 'close parenthesis',
    '``': 'open quote',
    ',': 'comma',
    "''": 'close quote',
    '.': 'period',
    '#': 'currency',
    '$': 'currency',
    ':': 'colon',
    'SYM': 'Symbol',
    'CC': 'conjunction',
    'CD': 'digit',
    'DT': 'determiner',
    'EX': 'there',
    'FW': 'foreign',
    'IN': 'preposition',
    'JJ': 'adjective',
    'JJR': 'adjective',
    'JJS': 'adjective',
    'LS': 'list marker',
    'MD': 'modal',
    'NN': 'noun',
    'NNS': 'noun',
    'NNP': 'proper noun',
    'NNPS': 'proper noun',
    'PDT': 'predeterminer',
    'POS': 'possessive',
    'PRP': 'pronoun',
    'PRP$': 'pronoun',
    'RB': 'adverb',
    'RBR': 'adverb',
    'RBS': 'adverb',
    'RP': 'particle',
    'TO': 'to',
    'UH': 'interjection',
    'VB': 'verb',
    'VBD': 'verb',
    'VBG': 'verb',
    'VBN': 'verb',
    'VBP': 'verb',
    'VBZ': 'verb',
    'WDT': 'wh-determiner',
    'WP': 'wh-pronoun',
    'WP$': 'wh-pronoun',
    'WRB': 'wh-abverb'
}


ANALYSIS_VERSION = '7'
TOKEN_VERSION = '2'
BASE_DATA_PATH = '/opt/mauve/' if os.getenv('TEST_ENV', 'False') == 'False' else '/tmp/mauve'
GOODREADS_METADATA_PATH = os.path.join(BASE_DATA_PATH, 'metadata')
TEXT_PATH = os.path.join(BASE_DATA_PATH, 'txt')
EPUB_PATH = os.path.join(BASE_DATA_PATH, 'epub')
CLEAN_EPUB_PATH = os.path.join(BASE_DATA_PATH, 'clean_books')
OIREACHTAS_DIR = os.path.join(BASE_DATA_PATH, 'oireachtas')


SENTENCE_TERMINATORS = {'.', '?', '!'}


LIKELY_PERSON_PREFIXES = [
    'dr ',
    'mr ',
    'ms ',
    'mrs ',
    'miss '
]

GENDER_PREFIXES = {
    'mr': 'male',
    'mister': 'male',
    'mr.': 'male',
    'sir': 'male',
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

PERSON_PREFIXES = list(GENDER_PREFIXES.keys()) + list(PERSON_TITLE_PREFIXES.keys())

SPEECH_QUOTES = ['`', '‘', '"', '``', '\'\'']
