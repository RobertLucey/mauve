import copy
from mauve.models.deptree import DepTree
from mauve.models.meaning_tree import Node


class Assignment():

    def __init__(self, sentence, p, n, c):
        """

        :param sentence: The full sentence object for some context
        :param p: previous phrase (this)
        :param n: next phrase (silly)
        :param c: current phrase (is)
        useful, prob goint to remove
        """
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



# TODO: only extract first assignment, then feed the tail into a parser that may analyse again in the tree
def extract_assignments(sentence, get_node=False):
    """
    Given segments, pull out the assignments made in the segments

    :param sentence: Sentence object
    :kwarg get_node:
    :return:
    """

    if get_node:
        if sentence is None:
            return Node(None)

    if get_node:
        if sentence.value is None:
            return Node(None)

    joining_words = ['is', 'are', 'am', 'was', 'were', 'be']

    good = False
    for joining_word in joining_words:
        if get_node:
            text = sentence.value.text
        else:
            text = sentence.text
        if ' ' + joining_word + ' ' in text:
            good = True
            break

    if not good:
        return Node(None)

    if get_node:
        deptree = sentence.value.deptree
    else:
        deptree = sentence.deptree

    assignments = []

    # Still interesting things around -ly and wordy things

    for equal_node in deptree.equals:

        # expl can usually be second part of an assignment?

        left = deptree.get_closest_before(
            equal_node,
            dep=['nsubj', 'dobj', 'pobj', 'nsubj', 'expl']
        )

        if get_node:
            people = sentence.value.people
        else:
            people = sentence.people

        if all([
            not left.segment.is_noun,
            not left.segment.is_prp,
            left.segment.text not in people,
            left.dep not in ['nsubj', 'dobj', 'pobj', 'nsubj', 'expl']
        ]):
            continue

        if get_node:
            from mauve.models.sentence import Sentence

            new = Node(equal_node)
            new.left = Node(left)
            new.right = Node(Sentence(' '.join([d.text for d in deptree.get_after_node(equal_node)])))  #Sentence(' '.join([a.text for a in deptree.get_after_node(equal_node)]))  # TODO: recurse with conditionals and all that
            return new

        else:
            assignments.append(
                Assignment(
                    sentence,
                    left.segment,
                    DepTree(deptree.get_after_node(equal_node)),
                    equal_node
                )
            )

    if not get_node:
        return assignments
