from functools import lru_cache

import spacy

from spacy_wordnet.wordnet_annotator import WordnetAnnotator

from cached_property import cached_property


class Synonym():

    @lru_cache(maxsize=100000)
    def get_word(self, text):
        if ' ' in text:
            return text
        else:
            try:

                token = self.nlp(text)[0]

                token._.wordnet.synsets()
                token._.wordnet.lemmas()
                token._.wordnet.wordnet_domains()

                return sorted(
                    token._.wordnet.wordnet_synsets_for_domain(['finance', 'banking'])[0].lemma_names()
                )[0]
            except:
                return text

    @cached_property
    def nlp(self):
        nlp = spacy.load('en')
        nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')
        return nlp
