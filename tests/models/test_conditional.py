from unittest import TestCase
import mock

import glob
import os

from mauve.structure.conditional import parse_conditionals
from mauve.models.sentence import Sentence


class TestConditional(TestCase):

    def test_parse_from_sentence(self):

        node = parse_conditionals(
            Sentence('If you went to bed earlier, you\'d be better rested')
        )[0]
        self.assertEqual(node[0].text, 'If you went to bed earlier')  # Forget about the extra if for the moment
        self.assertEqual(node[1].text, 'If')
        self.assertEqual(node[2].text, 'you \'d be better rested')

        node = parse_conditionals(
            Sentence('If and only if something then something')
        )[0]
        self.assertEqual(node[0].text, 'If and only if something')
        self.assertEqual(node[1].text, 'If')
        self.assertEqual(node[2].text, 'something')

        #node = parse_conditionals(
        #    Sentence('You can have some chocolate if you like')
        #)[0]
        #self.assertEqual(node.left.text, 'you like')
        #self.assertEqual(node.value.text, 'If')
        #self.assertEqual(node.right.text, 'You can have some chocolate')

