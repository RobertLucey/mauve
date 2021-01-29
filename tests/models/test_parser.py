from unittest import TestCase

from mauve.parser import get_back

from mauve.models.sentence import Sentence
from mauve.models.meaning_tree import Node



class Testparser(TestCase):

    def test_parser(self):
        root = Node(
            None
        )
        root.right = Node(Sentence('This is a weird test if it was failing'))

        the_back = get_back(root)

        # good things only come from the right hand side
        self.assertIsNone(the_back.left)
        self.assertIsNone(the_back.value)

        self.assertEquals(
            the_back.right.serialize(),

{'left': {'left': None,
          'right': None,
          'value': {'children': [],
                    'dep': 'nsubj',
                    'head': 'is',
                    'pos': 'AUX',
                    'segment': {'lem_stem': 'thi',
                                'tag': 'AUX',
                                'text': 'This'},
                    'text': 'This'}},
 'right': {'left': {'left': None,
                    'right': None,
                    'value': {'children': [],
                              'dep': 'nsubj',
                              'head': 'was',
                              'pos': 'AUX',
                              'segment': {'lem_stem': 'it',
                                          'tag': 'AUX',
                                          'text': 'it'},
                              'text': 'it'}},
           'right': {'left': None,
                     'right': {'left': None, 'right': None, 'value': None},
                     'value': {'people': [], 'text': 'failing'}},
           'value': {'children': [{'children': [],
                                   'dep': 'mark',
                                   'head': 'was',
                                   'idx': 17,
                                   'pos': 87,
                                   'text': 'if'},
                                  {'children': [],
                                   'dep': 'nsubj',
                                   'head': 'was',
                                   'idx': 20,
                                   'pos': 87,
                                   'text': 'it'},
                                  {'children': [],
                                   'dep': 'acomp',
                                   'head': 'was',
                                   'idx': 27,
                                   'pos': 87,
                                   'text': 'failing'}],
                     'dep': 'advcl',
                     'head': 'strange___test',
                     'pos': 'ADJ',
                     'segment': {'lem_stem': 'wa', 'tag': 'ADJ', 'text': 'was'},
                     'text': 'was'}},
 'value': {'children': [{'children': [],
                         'dep': 'nsubj',
                         'head': 'is',
                         'idx': 0,
                         'pos': 87,
                         'text': 'This'},
                        {'children': [{'children': [],
                                       'dep': 'det',
                                       'head': 'strange___test',
                                       'idx': 8,
                                       'pos': 84,
                                       'text': 'a'}],
                         'dep': 'attr',
                         'head': 'is',
                         'idx': 10,
                         'pos': 87,
                         'text': 'strange___test'},
                        {'children': [{'children': [],
                                       'dep': 'mark',
                                       'head': 'failing',
                                       'idx': 25,
                                       'pos': 100,
                                       'text': 'if'},
                                      {'children': [],
                                       'dep': 'nsubj',
                                       'head': 'failing',
                                       'idx': 28,
                                       'pos': 100,
                                       'text': 'it'},
                                      {'children': [],
                                       'dep': 'aux',
                                       'head': 'failing',
                                       'idx': 31,
                                       'pos': 100,
                                       'text': 'was'}],
                         'dep': 'advcl',
                         'head': 'is',
                         'idx': 35,
                         'pos': 87,
                         'text': 'failing'}],
           'dep': 'ROOT',
           'head': 'is',
           'pos': 'AUX',
           'segment': {'lem_stem': 'is', 'tag': 'AUX', 'text': 'is'},
           'text': 'is'}}
        )
