from unittest import TestCase
import mock

import glob
import os

from mauve.structure.conditional import extract_conditionals
from mauve.models.sentence import Sentence


class TestConditional(TestCase):

    def test_extract_from_sentence(self):

        node = extract_conditionals(
            Sentence('If you went to bed earlier, you\'d be better rested')
        )[0]
        self.assertEqual(node[0].text, 'If you went to bed earlier')  # Forget about the extra if for the moment
        self.assertEqual(node[1].text, 'If')
        self.assertEqual(node[2].text, 'you \'d be better rested')

        node = extract_conditionals(
            Sentence('If and only if something then something')
        )[0]
        self.assertEqual(node[0].text, 'If and only if something')
        self.assertEqual(node[1].text, 'If')
        self.assertEqual(node[2].text, 'something')

        node = extract_conditionals(
            Sentence('You can have some chocolate if you want')
        )[0]
        self.assertEqual(node[0].text, 'you want')
        self.assertEqual(node[1].text, 'if')
        self.assertEqual(node[2].text, 'You can have some chocolate')

    def test_as_long_as(self):
        node = extract_conditionals(
            Sentence('as long as you fed him, he would be cooperative')
        )[0]
        self.assertEqual(node[0].text, 'as_long_as you fed him')
        self.assertEqual(node[1].text, 'as long as')
        self.assertEqual(node[2].text, 'he would be cooperative')
