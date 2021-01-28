from mauve.utils import (
    lower,
    previous_current_next
)

from mauve.models.deptree import DepTree, DepNode


class Assignment():

    def __init__(self, sentence, p, n, c):
        '''

        :param sentence: The full sentence object for some context
        :param p: previous phrase (this)
        :param n: next phrase (silly)
        :param c: current phrase (is)
        useful, prob goint to remove
        '''
        self.sentence = sentence
        self.p = p
        self.n = n
        self.c = c

    def serialize(self):
        return {
            'p': self.p.serialize(),
            'n': self.n.serialize(),
            'c': self.c.serialize(),
            'sentence': self.sentence.serialize()
        }


def extract_assignments(sentence, use_deptree=True):
    '''
    Given a sentence, pull out the assignments made in the sentence

    :param sentence: Sentence object
    :kwarg use_deptree:
    :return:
    '''
    joining_words = ['is', 'are', 'am', 'was', 'were', 'be']

    good = False
    for joining_word in joining_words:
        if ' ' + joining_word + ' ' in sentence.text:
            good = True
            break

    if not good:
        return []

    deptree = sentence.deptree

    assignments = []

    # Still interesting things around -ly and wordy things

    for eq in deptree.equals:

        left = deptree.get_closest_before(eq, dep=['nsubj', 'dobj', 'pobj', 'nsubj'])

        if not left.segment.is_noun and not left.segment.is_prp and left.segment.text not in sentence.people and left.dep not in ['nsubj', 'dobj', 'pobj', 'nsubj']:
            continue

        assignments.append(
            Assignment(
                sentence,
                left.segment,
                DepTree(deptree.get_after_node(eq)),
                eq
            )
        )
    return assignments
