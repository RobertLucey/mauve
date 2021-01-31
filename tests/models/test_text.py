from unittest import TestCase
import mock

from collections import Counter
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


RESOURCE_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    ),
    'tests/resources'
)


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

    def test_people_titles(self):
        people = TextBody(
            content='Mr C Lucey went to the shop. He then saw Dr O\'Malley talking to Mr Somethingorother.'
        ).people

        self.assertEqual(
            sorted([p.name for p in people]),
            sorted(["Dr O'Malley", 'Mr C Lucey', 'Mr Somethingorother'])
        )

    def test_alice(self):
        alice = open(os.path.join(RESOURCE_PATH, 'alices_adventures_in_wonderland.txt'), 'r').read()
        book = TextBody(content=alice)
        people_names = [p.name for p in book.people]
        print(people_names)
        print(set(people_names))
        self.assertTrue('Alice' in people_names)
        self.assertTrue('Hatter' in people_names)
        self.assertTrue('March Hare' in people_names)
        self.assertTrue('Ada' in people_names)
        self.assertTrue('Caterpillar' in people_names)  # since it's a noun. Should be able to extract because the Caterpillar speaks
