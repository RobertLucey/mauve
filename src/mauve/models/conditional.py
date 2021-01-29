CONDITIONAL_LIST = [
    'if',
    'because',
    'as long as',
    'whenever'  # loose
]


class Conditional():

    def __init__(self, word, subject=None, conjunction=None):
        '''
        (If)word (you went to bed earlier)subject, (you'd be better rested)conjunction
        '''
        self.word = word
        self.subject = subject
        self.conjunction = conjunction

    @staticmethod
    def parse_conditionals(sentence):
        from mauve.models.sentence import Sentence

        conditionals = []
        for conditional in sentence.deptree.conditionals:

            value = conditional
            if conditional.idx == 0:
                left = Sentence(
                    ' '.join(
                        [
                            s.text for s in sentence.deptree.get_before_node(sentence.deptree.get_closest_after(conditional, text=[',', 'then']))
                        ]
                    )
                )
                right = Sentence(
                    ' '.join(
                        [
                            s.text for s in sentence.deptree.get_after_node(sentence.deptree.get_closest_after(conditional, text=[',', 'then']))
                        ]
                    )
                )

                conditionals.append(
                    (left, value, right)
                )
            else:
                print('conditional not at start')

        return conditionals
