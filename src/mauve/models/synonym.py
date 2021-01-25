import spacy

from spacy_wordnet.wordnet_annotator import WordnetAnnotator

from cached_property import cached_property


class Synonym():


    def mod_word(self):

        if ' ' in self.text:
            return self.text
        else:
            try:

                token = self.nlp(self.text)[0]

                token._.wordnet.synsets()
                token._.wordnet.lemmas()
                token._.wordnet.wordnet_domains()

                self.text = sorted(
                    token._.wordnet.wordnet_synsets_for_domain(['finance', 'banking'])[0].lemma_names()
                )[0]
            except:
                pass


    @cached_property
    def nlp(self):
        nlp = spacy.load('en')
        nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')
        return nlp
