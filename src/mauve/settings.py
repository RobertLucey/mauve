import os

WORDNET_REPLACE = eval(os.getenv('WORDNET_REPLACE', 'False'))
HE_SHE_SPEAKER_GUESS = eval(os.getenv('HE_SHE_SPEAKER_GUESS', 'True'))
SPEAKER_PLACEMENT_GUESS = eval(os.getenv('SPEAKER_PLACEMENT_GUESS', 'True'))

PREPROCESS_NORMALIZE_SPELLING = eval(os.getenv('PREPROCESS_NORMALIZE_SPELLING', 'True'))
PREPROCESS_NUMBER_CONVERT = eval(os.getenv('PREPROCESS_NUMBER_CONVERT', 'True'))
