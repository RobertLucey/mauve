import random

from nltk.tag.perceptron import PerceptronTagger


TAGGER = PerceptronTagger()


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
