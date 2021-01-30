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

    def test_text_body(self):

        people = TextBody(
            content='Robert went to the shop. He then saw Carl talking to Mark.'
        ).people

        self.assertEqual([p.name for p in people], ['Robert', 'Carl', 'Mark'])
