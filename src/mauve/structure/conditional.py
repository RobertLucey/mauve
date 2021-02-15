CONDITIONAL_LIST = [
    'if',
    'as long as',  # loose - "they have been there as long as anyone can remember"
    'so long as',
    'in case',  # might want to think about this one
    'provided',  # loose
    'providing',  # loose
    'unless',  # neg
    'suppose',  # only at start of sentence?
]


def extract_conditionals(sentence):
    '''

    If clause (condition)
    If + past perfect

    '''
    from mauve.models.sentence import Sentence

    conditionals = []
    for conditional in sentence.deptree.conditionals:

        value = conditional
        if conditional.idx == 0:
            left = Sentence(
                ' '.join(
                    [
                        s.text for s in sentence.deptree.get_before_node(
                            sentence.deptree.get_closest_after(
                                conditional,
                                text=[',', 'then']
                            )
                        )
                    ]
                )
            )
            right = Sentence(
                ' '.join(
                    [
                        s.text for s in sentence.deptree.get_after_node(
                            sentence.deptree.get_closest_after(
                                conditional,
                                text=[',', 'then']
                            )
                        )
                    ]
                )
            )

            conditionals.append(
                (left, value, right)
            )
        else:

            right = Sentence(
                ' '.join(
                    [
                        s.text for s in sentence.deptree.get_before_node(
                            conditional
                        )
                    ]
                )
            )
            left = Sentence(
                ' '.join(
                    [
                        s.text for s in sentence.deptree.get_after_node(
                            conditional
                        )
                    ]
                )
            )

            conditionals.append(
                (left, value, right)
            )

    return conditionals
