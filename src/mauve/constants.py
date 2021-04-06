import os
import json
import string

from mauve.profanity import PROFANITY_LIST

import nltk
from nltk.corpus import words


PADDED_PROFANITY_LIST = [' ' + p + ' ' for p in PROFANITY_LIST]

ENG_WORDS = set(nltk.corpus.words.words())

LIKELY_WORD_TOKENS = [
    'CC',
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
AUTHOR_METADATA_PATH = os.path.join(GOODREADS_METADATA_PATH, 'author_metadata.json')
TEXT_PATH = os.path.join(BASE_DATA_PATH, 'txt')
EPUB_PATH = os.path.join(BASE_DATA_PATH, 'epub')
CLEAN_EPUB_PATH = os.path.join(BASE_DATA_PATH, 'clean_books')
OIREACHTAS_DIR = os.path.join(BASE_DATA_PATH, 'oireachtas')


SENTENCE_TERMINATORS = {'.', '?', '!'}
SPEECH_QUOTES = {'`', '‘', '"', '``', '”', '“', '’'}
EXTENDED_PUNCTUATION = list(string.punctuation) + list(SPEECH_QUOTES)


LIKELY_PERSON_PREFIXES = {
    'dr',
    'mr',
    'ms',
    'mrs',
    'miss',
    'sir'
}

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

NLTK_ENG_WORDS = set(words.words())


REPLACEMENTS = {
    'a great help': 'helpful',
    'absolutely necessary': 'necessary',
    'in regard to': 'regarding',
    'in regards to': 'regarding',
    'i\'m': 'i am',
    'a bit difficult': 'difficult',
    'per annum': 'yearly',
    'a good thing': 'good',
    'sinn féin': 'sinn_fein',
    'don\'t': 'do not',
    'it\'s': 'it is',
    'a great deal': 'a lot',
    'fully aware': 'aware',
    'motor car': 'car',
    'mr.': 'mr',
    'mrs.': 'mrs',
    'dr.': 'dr',
    'ms.': 'ms',
    'Mr.': 'Mr',
    'Mrs.': 'Mrs',
    'Dr.': 'Dr',
    'Ms.': 'Ms',
    'in favour': 'in_favour',
    'general election': 'general_election',
    'reap the benefit': 'benefit',
    'much longer': 'much_longer',
    'a great help': 'helpful',
    'absolutely necessary': 'necessary',
    'in regard to': 'regarding',
    'in regards to': 'regarding',
    'i\'m': 'i am',
    'a bit difficult': 'difficult',
    'per annum': 'yearly',
    'a good thing': 'good',
    'sinn féin': 'sinn_fein',
    'don\'t': 'do not',
    'it\'s': 'it is',
    'a great deal': 'a lot',
    'fully aware': 'aware',
    'motor car': 'car',

    # need to do by word so these one word ones can be used
    #'yeah': 'yes',
    #'yep': 'yes',
    #'nope': 'no',
    #'nah': 'no',
    #'da': 'father',
    #'dad': 'father',
    #'daddy': 'father',
    #'ma': 'mother',
    #'mum': 'mother',
    #'mam': 'mother',
    #'mammy': 'mother'
}  # TODO: test this

for k, v in REPLACEMENTS.copy().items():
    REPLACEMENTS[k.capitalize()] = v.capitalize()
