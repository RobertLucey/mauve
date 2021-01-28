from unittest import TestCase

from mauve import ENCORE

from mauve.models.deptree import DepNode, DepTree


class TestDepNode(TestCase):

    def test_serialize(self):
        token = ENCORE('window')[0]
        node = DepNode(
            token.text,
            token.dep_,
            token.head.text,
            token.head.pos_,
            [child for child in token.children],
            token.idx
        )

        self.assertEquals(
            node.serialize(),
            {
                'text': 'window',
                'dep': 'ROOT',
                'head': 'window',
                'pos': 'NOUN',
                'children': [],
                'segment': {
                    'text': 'window',
                    'tag': 'NOUN',
                    'lem_stem': 'window'
                }
            }
        )


class TestDepTree(TestCase):

    def test_text(self):
        doc = ENCORE('The window is cold')
        tree = DepTree([
            DepNode(
                token.text,
                token.dep_,
                token.head.text,
                token.head.pos_,
                [child for child in token.children],
                token.idx
            ) for token in doc
        ])

        self.assertEqual(
            tree.text,
            'The window is cold'
        )

    def test_get_after_node(self):
        doc = ENCORE('The window is cold')

        tree = DepTree([
            DepNode(
                token.text,
                token.dep_,
                token.head.text,
                token.head.pos_,
                [child for child in token.children],
                token.idx
            ) for token in doc
        ])

        after = tree.get_after_node(tree.nodes[1])
        self.assertEquals(' '.join([n.text for n in after]), 'is cold')

    def test_equals(self):
        doc = ENCORE('The window is cold')

        tree = DepTree([
            DepNode(
                token.text,
                token.dep_,
                token.head.text,
                token.head.pos_,
                [child for child in token.children],
                token.idx
            ) for token in doc
        ])
        self.assertEquals(len(tree.equals), 1)
        self.assertEquals(tree.equals[0].text, 'is')

    def test_closest_before(self):
        doc = ENCORE('The window is cold')

        tree = DepTree([
            DepNode(
                token.text,
                token.dep_,
                token.head.text,
                token.head.pos_,
                [child for child in token.children],
                token.idx
            ) for token in doc
        ])

        self.assertEquals(
            tree.get_closest_before(tree.nodes[2], dep=['det']).text,
            'The'
        )
        self.assertEquals(
            tree.get_closest_before(tree.nodes[2], dep=['nsubj']).text,
            'window'
        )

    def test_serialize(self):
        doc = ENCORE('The window is cold')
        tree = DepTree([
            DepNode(
                token.text,
                token.dep_,
                token.head.text,
                token.head.pos_,
                [child for child in token.children],
                token.idx
            ) for token in doc
        ])

        self.assertEquals(
            tree.serialize(),
            [{'children': [],
              'dep': 'det',
              'head': 'window',
              'pos': 'NOUN',
              'segment': {'lem_stem': 'the', 'tag': 'NOUN', 'text': 'The'},
              'text': 'The'},
             {'children': [{'children': [],
                            'dep': 'det',
                            'head': 'window',
                            'idx': 0,
                            'pos': 92,
                            'text': 'The'}],
              'dep': 'nsubj',
              'head': 'is',
              'pos': 'AUX',
              'segment': {'lem_stem': 'window', 'tag': 'AUX', 'text': 'window'},
              'text': 'window'},
             {'children': [{'children': [{'children': [],
                                          'dep': 'det',
                                          'head': 'window',
                                          'idx': 0,
                                          'pos': 92,
                                          'text': 'The'}],
                            'dep': 'nsubj',
                            'head': 'is',
                            'idx': 4,
                            'pos': 87,
                            'text': 'window'},
                           {'children': [],
                            'dep': 'acomp',
                            'head': 'is',
                            'idx': 14,
                            'pos': 87,
                            'text': 'cold'}],
              'dep': 'ROOT',
              'head': 'is',
              'pos': 'AUX',
              'segment': {'lem_stem': 'is', 'tag': 'AUX', 'text': 'is'},
              'text': 'is'},
             {'children': [],
              'dep': 'acomp',
              'head': 'is',
              'pos': 'AUX',
              'segment': {'lem_stem': 'cool', 'tag': 'AUX', 'text': 'cool'},
              'text': 'cold'}]
        )
