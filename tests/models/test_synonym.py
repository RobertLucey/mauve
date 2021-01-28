from unittest import TestCase
import mock

import glob
import os

from mauve.models.segment import Segment
from mauve.models.sentence import Sentence
from mauve.models.books.book import Book
from mauve.models.books.review import Reviews, Review
from mauve.models.books.tag import Tags, Tag
from mauve import constants

from mauve.models.synonym import Synonym


class TestSynonym(TestCase):

    def test_synonym(self):

        s = Synonym()
        self.assertEqual(s.get_word('large'), 'big')
        self.assertEqual(s.get_word('asdasdasd'), 'asdasdasd')
