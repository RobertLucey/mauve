from unittest import TestCase
import mock

import glob
import os

from mauve.models.text import TextBody
from mauve.models.segment import Segment
from mauve.models.sentence import Sentence
from mauve.models.books.book import Book
from mauve.models.books.review import Reviews, Review
from mauve.models.books.tag import Tags, Tag
from mauve import constants

from mauve.models.synonym import Synonym


class TestTextBody(TestCase):

    def test_people_firstnames(self):

        people = TextBody(
            content='Robert went to the shop. He then saw Carl talking to Mark.'
        ).people

        self.assertEqual(
            sorted([p.name for p in people]),
            sorted(['Robert', 'Carl', 'Mark'])
        )

    def test_people_fullnames(self):

        people = TextBody(
            content='Robert Lucey went to the shop. He then saw Carl O\'Malley talking to Mark Somethingorother.'
        ).people

        self.assertEqual(
            sorted([p.name for p in people]),
            sorted(['Carl O\'Malley', 'Mark Somethingorother', 'Robert Lucey'])
        )

    def test_people_fullnames_initials(self):

        people = TextBody(
            content='Robert C Lucey went to the shop. He then saw Carl O\'Malley talking to Mark M. Somethingorother.'
        ).people

        self.assertEqual(
            sorted([p.name for p in people]),
            sorted(['Carl O\'Malley', 'Mark M. Somethingorother', 'Robert C Lucey'])
        )
