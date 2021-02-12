from unittest import TestCase
import mock

from collections import Counter
import glob
import os

from mauve.utils import flatten
from mauve.models.text import TextBody
from mauve.models.person import Person
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

    ALICE = TextBody(content=open(os.path.join(RESOURCE_PATH, 'alices_adventures_in_wonderland.txt'), 'r').read())

    def test_people_firstnames(self):
        people = TextBody(
            content='Robert went to the shop. He then saw Carl talking to Mark.'
        ).people

        self.assertEqual(
            sorted([p.name for p in people]),
            sorted(['Robert', 'Carl', 'Mark'])
        )

    def test_people_firstnames_multi_speech(self):
        people = TextBody(content='“You are not attending!” said the Mouse to Alice severely. “What are you thinking of?”').people

        self.assertEqual(
            sorted([p.name for p in people]),
            sorted(['Mouse', 'Alice'])
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
            sorted(["O'Malley", 'C Lucey', 'Somethingorother']),
        )

    def test_alice_people(self):
        people_names = [p.name for p in self.ALICE.people]
        all_names = 'all names: %s' % people_names
        self.assertTrue('Alice' in people_names, all_names)
        self.assertTrue('Hatter' in people_names, all_names)
        self.assertTrue('March Hare' in people_names, all_names)
        self.assertTrue('Ada' in people_names, all_names)
        #self.assertTrue('Caterpillar' in people_names, all_names)  # since it's a noun. Should be able to extract because the Caterpillar speaks

    def test_alice_assignments(self):
        alice_assignments = []
        for sentence_assignments in self.ALICE.assignments:
            for assignment in sentence_assignments:
                if 'alice' in assignment[0].text.lower():
                    alice_assignments.append(assignment[2].text)
        # First assignment in the book
        self.assertTrue(
            alice_assignments[0].startswith('beginning to get very tired of sitting by her sister')
        )

    def test_alice_speech(self):
        speech_objects = self.ALICE.get_speech_by_people([Person(name='Alice')])
        print(speech_objects)
        
        self.assertTrue(
            'Who cares for you ?' in [s.text for s in speech_objects['Alice']]
        )

    def test_sentiment_by_person(self):
        sentiment_by_person = self.ALICE.get_sentiment_by_people(people=[Person(name='Alice'), Person(name='Queen')])

        self.assertGreater(
            sentiment_by_person['Alice']['compound'],
            0.5
        )
        self.assertLess(
            sentiment_by_person['Queen']['compound'],
            -0.5
        )

    def test_words(self):
        self.assertEqual(
            TextBody(content='I\'m here now.').words,
            ['I', 'am', 'here', 'now']
        )

        self.assertEqual(
            TextBody(content='“Jekyll,” said Utterson,').words,
            ['Jekyll', 'said', 'Utterson']
        )


    def test_lang(self):
        self.assertEqual(
            TextBody(content='I like to ride my bicycle.').lang,
            'en'
        )
        self.assertEqual(
            TextBody(content='Encantado de conocerte.').lang,
            'es'
        )

    def test_get_assignments_by(self):
        self.assertEqual(
            TextBody(content='Ducks are cute. You are ugly').get_assignments_by('ducks'),
            ['cute']
        )
        self.assertEqual(
            TextBody(content='Ducks are cute. You are ugly').get_assignments_by('you'),
            ['ugly']
        )
