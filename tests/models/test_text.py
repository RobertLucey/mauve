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

    def test_alice_people(self):
        alice = open(os.path.join(RESOURCE_PATH, 'alices_adventures_in_wonderland.txt'), 'r').read()
        book = TextBody(content=alice)
        people_names = [p.name for p in book.people]
        self.assertTrue('Alice' in people_names)
        self.assertTrue('Hatter' in people_names)
        self.assertTrue('March Hare' in people_names)
        self.assertTrue('Ada' in people_names)
        #self.assertTrue('Caterpillar' in people_names)  # since it's a noun. Should be able to extract because the Caterpillar speaks

    def test_alice_assignments(self):
        alice = open(os.path.join(RESOURCE_PATH, 'alices_adventures_in_wonderland.txt'), 'r').read()
        book = TextBody(content=alice)
        alice_assignments = []
        for sentence_assignments in book.assignments:
            for assignment in sentence_assignments:
                if 'alice' in assignment[0].text.lower():
                    alice_assignments.append(assignment[2].text)
        # First assignment in the book
        self.assertTrue(
            alice_assignments[0].startswith('beginning to get very tired of sitting by her sister')
        )

    #def test_alice_speech(self):
    #    alice = open(os.path.join(RESOURCE_PATH, 'alices_adventures_in_wonderland.txt'), 'r').read()

    #    book = TextBody(content=alice)
    #    print([s.serialize() for s in book.speech if s])
    #    raise Exception()
    #    #speech_objects = book.get_speech_by_person(Person(name='Alice'))
    #    #self.assertTrue(
    #    #    {'text': 'which certainly was not here before ,', 'speaker': {'name': 'Alice', 'gender': 'female'}, 'inflection': 'said'} in [s.serialize() for s in speech_objects]
    #    #)

    #def test_sentiment_person(self):
    #    alice = open(os.path.join(RESOURCE_PATH, 'alices_adventures_in_wonderland.txt'), 'r').read()

    #    book = TextBody(content=alice)
    #    sentiment_by_person = book.get_sentiment_by_person()


    #    for person_name, lines in sentiment_by_person.items():
    #        print(lines)
    #        print('%s  -  %s' % (person_name, TextBody(content=' .'.join(lines)).sentiment))

    #    raise Exception()

    def test_get_text(self):
        content = '''
        Alice folded her hands, and began:—

“You are old, Father William,” the young man said,
    “And your hair has become very white;
And yet you incessantly stand on your head—
    Do you think, at your age, it is right?”

        '''

        book = TextBody(content=content)
        # [{'text': 'You are old , Father William ,', 'speaker': {'name': 'young man', 'gender': None}, 'inflection': 'said'}, {'text': 'And your hair has become very white ; And yet you incessantly stand on your head— Do you think , at your age , it is right ?', 'speaker': {'name': '', 'gender': None}, 'inflection': 'said'}]
