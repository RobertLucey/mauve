from unittest import TestCase
import mock

import glob
import os

from mauve.models.text import Sentence, Segment
from mauve.models.books.book import Book
from mauve.models.books.review import Reviews, Review
from mauve.models.books.tag import Tags, Tag
from mauve import constants


class TestSentence(TestCase):

    def test_segments(self):
        s = Sentence('This is a sentence.')
        self.assertEqual(
            [o.text for o in s.segments],
            ['This', 'is', 'a', 'sentence', '.']
        )

        # since voluntary groups is a joining phrase
        s = Sentence('Can you please do something about voluntary groups?')
        self.assertEqual(
            [o.text for o in s.segments],
            ['Can', 'you', 'please', 'do', 'something', 'about', 'voluntary groups', '?']
        )

        s = Sentence('The first about dog food')
        self.assertEqual(
            [o.text for o in s.segments],
            ['The', 'first', 'about', 'dog food']
        )
        self.assertEqual(
            [o.tag for o in s.segments],
            ['DT', 'ORDINAL', 'IN', 'dunno']
        )


class TestSegment(TestCase):

    def test_tag(self):
        self.assertEqual(
            Segment('blah', tag='wooooo').tag,
            'wooooo'
        )
        self.assertEqual(
            Segment('I').tag,
            'PRP'
        )
        self.assertEqual(
            Segment('a phrase').tag,
            'dunno'
        )

    def test_is_entity(self):
        self.assertTrue(Segment('asd.', tag='DATE').is_entity)
        self.assertFalse(Segment('asd.', tag='NN').is_entity)

    def test_is_word(self):
        self.assertFalse(Segment('asd.').is_wordy)
        self.assertFalse(Segment('asd,').is_wordy)
        self.assertTrue(Segment('asd ').is_wordy)

    def test_lem(self):
        self.assertEqual(Segment('bats').lem, 'bat')
