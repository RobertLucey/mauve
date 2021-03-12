import nltk


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
