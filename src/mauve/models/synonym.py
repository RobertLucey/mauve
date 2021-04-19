from functools import lru_cache
from collections import defaultdict
import operator
import logging
from typing import Mapping

from mauve.settings import WORDNET_REPLACE
from mauve.constants.synonym import (
    CUSTOM_SYNONYMS,
    SYNONYM_SKIP_WORDS
)

logger = logging.getLogger('mauve')


ALL = defaultdict(int)


class Synonym:

    @staticmethod
    def get_word(text: str) -> str:
        attempt = CUSTOM_SYNONYMS.get(text, None)
        if attempt is not None:
            return attempt
        ALL[text] += 1
        # if there aren't enugh words already processed then don't trust the ALL since it is cold
        return Synonym._get_word(text)

    @staticmethod
    def get_synonyms(word: str, method='wordnet') -> Mapping[str, int]:
        if method == 'wordnet':

            from mauve.utils import get_en_core_web_sm
            token = get_en_core_web_sm(word)[0]

            token._.wordnet.synsets()
            token._.wordnet.lemmas()
            token._.wordnet.wordnet_domains()

            domains = ['book_keeping', 'military', 'diplomacy', 'time_period', 'social_science', 'social', 'humanities', 'health', 'geology', 'economy', 'statistics', 'enterprise', 'agriculture', 'law', 'money', 'sport', 'school', 'environment', 'transport', 'politics', 'medicine', 'telecommunication', 'tourism', 'banking', 'town_planning', 'administration', 'insurance', 'finance', 'pharmacy', 'commerce', 'tax']

            options = {word: ALL[word]}
            for domain in token._.wordnet.wordnet_synsets_for_domain(domains):
                for name in domain.lemma_names():
                    options[name] = ALL.get(name, 0)
        else:
            options = {word: ALL[word]}

        return options

    @staticmethod
    @lru_cache(maxsize=100000)
    def _get_word(text: str) -> str:

        if text in SYNONYM_SKIP_WORDS:
            return text

        if ' ' in text:
            return text

        try:
            if WORDNET_REPLACE:
                options = Synonym(text, method='wordnet')
            else:
                options = Synonym(text, method=None)
            try:
                word = max(options.items(), key=operator.itemgetter(1))[0]

                if text.islower() and not word.islower():
                    word = word.lower()

                if word != text:
                    logger.debug('Synonym \'%s\' => \'%s\'', text, word)

                return word
            except:
                return text
        except:
            return text
