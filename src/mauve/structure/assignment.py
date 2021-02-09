import copy

from mauve.models.deptree import DepTree
from mauve.constants import ASSIGNMENT_WORDS


# TODO: only extract first assignment, then feed the tail into a parser that may analyse again in the tree
def extract_assignments(sentence):
    """
    Given segments, pull out the assignments made in the segments

    :param sentence: Sentence object
    :return:
    """

    good = False
    for joining_word in ASSIGNMENT_WORDS:
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

        people = sentence.people

        if all([
            not left.segment.is_noun,
            not left.segment.is_prp,
            left.segment.text not in people,
            left.dep not in ['nsubj', 'dobj', 'pobj', 'nsubj', 'expl']
        ]):
            continue

        from mauve.models.sentence import Sentence

        assignments.append(
            (
                left,
                equal_node,
                Sentence(' '.join([d.text for d in deptree.get_after_node(equal_node, stop_at_punct=True)]))
            )
        )

    return assignments
