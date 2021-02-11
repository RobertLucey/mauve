from unittest import TestCase
import mock

import glob
import os

from mauve.models.segment import Segment, Segments
from mauve.models.sentence import Sentence
from mauve.models.books.book import Book
from mauve.models.books.review import Reviews, Review
from mauve.models.books.tag import Tags, Tag
from mauve import constants

from mauve.models.synonym import Synonym


class TestSegments(TestCase):

    def test_vanity(self):
        segments = Segments()
        segments.extend([Segment('The'), Segment('end')])
        segments.append(Segment('is'))
        segments.append(Segment('nigh'))

        self.assertEqual(
            ' '.join([s.text for s in segments]),
            'The stop is nigh'
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

    def test_is_adj(self):
        self.assertTrue(
            Segment('big').is_adj
        )
        self.assertFalse(
            Segment('house').is_adj
        )

    def test_is_adv(self):
        self.assertTrue(
            Segment('very').is_adv
        )
        self.assertFalse(
            Segment('trumpet').is_adv
        )

    def test_is_verb(self):
        self.assertTrue(
            Segment('looking').is_verb
        )
        self.assertFalse(
            Segment('blue').is_verb
        )
        
    def test_is_entity(self):
        self.assertTrue(Segment('asd.', tag='DATE').is_entity)
        self.assertFalse(Segment('asd.', tag='NN').is_entity)

    def test_is_word(self):
        self.assertFalse(Segment('asd.').is_wordy)
        self.assertFalse(Segment('asd,').is_wordy)
        self.assertTrue(Segment('asd ').is_wordy)

    def test_lem_stem(self):
        self.assertEqual(Segment('bats').lem_stem, 'bat')
