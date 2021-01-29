import copy
from mauve.models.deptree import DepTree
from mauve.models.meaning_tree import Node


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



# TODO: only extract first assignment, then feed the tail into a parser that may analyse again in the tree
def extract_assignments(sentence, get_node=False):
    '''
    Given segments, pull out the assignments made in the segments

    :param segments: Segments object
    :kwarg get_node:
    :return:
    '''


    if get_node:

        node = sentence

        if node == None:
            return Node(None)

        if node.value == None:
            return Node(None)

        joining_words = ['is', 'are', 'am', 'was', 'were', 'be']

        good = False
        for joining_word in joining_words:
            if ' ' + joining_word + ' ' in node.value.text:
                good = True
                break

        if not good:
            return Node(None)

        deptree = node.value.deptree

        assignments = []

        # Still interesting things around -ly and wordy things

        for equal_node in deptree.equals:

            # expl can usually be second part of an assignment?

            left = deptree.get_closest_before(
                equal_node,
                dep=['nsubj', 'dobj', 'pobj', 'nsubj', 'expl']
            )

            if all([
                not left.segment.is_noun,
                not left.segment.is_prp,
                left.segment.text not in node.value.people,
                left.dep not in ['nsubj', 'dobj', 'pobj', 'nsubj', 'expl']
            ]):
                continue

            from mauve.models.sentence import Sentence

            new = Node(equal_node)
            new.left = Node(left)
            new.right = Node(Sentence(' '.join([d.text for d in deptree.get_after_node(equal_node)]))) #Sentence(' '.join([a.text for a in deptree.get_after_node(equal_node)]))  # TODO: recurse with conditionals and all that
            return new


    else:
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

        for equal_node in deptree.equals:

            # expl can usually be second part of an assignment?

            left = deptree.get_closest_before(
                equal_node,
                dep=['nsubj', 'dobj', 'pobj', 'nsubj', 'expl']
            )

            if all([
                not left.segment.is_noun,
                not left.segment.is_prp,
                left.segment.text not in sentence.people,
                left.dep not in ['nsubj', 'dobj', 'pobj', 'nsubj', 'expl']
            ]):
                continue

            if get_node:

                #assignment_node.right = Node(DepTree(deptree.get_after_node(equal_node)))  # TODO: recurse with conditionals and all that

                from mauve.models.sentence import Sentence
                # clean

                assignment_node = Node(equal_node)
                assignment_node.left = Node(left)
                assignment_node.right = Node(deptree.get_after_node(equal_node)) #Sentence(' '.join([a.text for a in deptree.get_after_node(equal_node)]))  # TODO: recurse with conditionals and all that

                return assignment_node

            else:
                assignments.append(
                    Assignment(
                        sentence,
                        left.segment,
                        DepTree(deptree.get_after_node(equal_node)),
                        equal_node
                    )
                )

        return assignments
