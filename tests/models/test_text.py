from unittest import TestCase
import mock

from collections import Counter
import glob
import os

from mauve.utils import flatten, rflatten
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



class TestTextBodyLine(TestCase):

    def test_lines_extract(self):
        lines = TextBody(
            content='''One two. Three.
            Four Five'''
        ).lines

        self.assertEquals(
            lines.serialize(),
            [
                {'text': 'One two. Three.', 'line_no': 0},
                {'text': 'Four Five', 'line_no': 1}
            ]
        )

    def test_multi_speakers_line(self):
        text = TextBody(
            content='''
“Bad no this sucks” said the Mouse to Alice. Alice replied, “Happy Love”
            '''
        )

        self.assertEqual(
            [s.serialize() for s in text.speech],
            [
                {'text': 'Bad no this sucks', 'speaker': {'name': 'Mouse', 'gender': None}, 'inflection': 'said'},
                {'text': 'Happy Love', 'speaker': {'name': 'Alice', 'gender': 'female'}, 'inflection': 'replied'},
            ]
        )

    def test_he_she_speech_extract(self):
        """Make sure only speech lines get context from -2 ago
        """
        text = TextBody(
            content='''
Mike asked, “Want some cheese?”
“I don’t know.” Alice’s response began, but ended in a whispered, “I really don't.”
“It's really tasty.” He went on
“It's really tasty.” He went on
            '''
        )

        self.assertEqual(
            [s.serialize() for s in text.speech],
            [
                {'text': 'Want some cheese ?', 'speaker': {'name': 'Mike', 'gender': 'male'}, 'inflection': 'asked'},
                {'text': 'I do not know .', 'speaker': {'name': 'Alice', 'gender': 'female'}, 'inflection': None},
                {'text': 'I really do not .', 'speaker': {'name': 'Alice', 'gender': 'female'}, 'inflection': 'whispered'},
                {'text': "It is really tasty .", 'speaker': {'name': 'Mike', 'gender': 'male'}, 'inflection': None},
                {'text': "It is really tasty .", 'speaker': {'name': 'Mike', 'gender': 'male'}, 'inflection': None},
            ]
        )

    def test_only_speech_lines_extract(self):
        """Make sure only speech lines get context from -2 ago
        """
        text = TextBody(
            content='''
Mike asked, “Want some cheese?”
“I don’t know.” Bob’s response began, but ended in a whispered, “I really don't.”
“It's really tasty.”
“But I'm lactose intolerant.” he said. “I don’t want to risk it.”
            '''
        )

        self.assertEqual(
            [s.serialize() for s in text.speech],
            [
                {'text': 'Want some cheese ?', 'speaker': {'name': 'Mike', 'gender': 'male'}, 'inflection': 'asked'},
                {'text': 'I do not know .', 'speaker': {'name': 'Bob', 'gender': 'male'}, 'inflection': None},
                {'text': 'I really do not .', 'speaker': {'name': 'Bob', 'gender': 'male'}, 'inflection': 'whispered'},
                {'text': "It is really tasty .", 'speaker': {'name': 'Mike', 'gender': 'male'}, 'inflection': None},
                {'text': 'But I am lactose intolerant .', 'speaker': {'name': 'Bob', 'gender': 'male'}, 'inflection': 'said'},
                {'text': 'I do not want to risk it .', 'speaker': {'name': 'Bob', 'gender': 'male'}, 'inflection': None}
            ]
        )

    def test_speech_extract_from_line(self):
        lines = TextBody(
            content='''
Mike asked, “Want some cheese?”
“I don’t know.” Bob’s response began, but ended in a whispered, “I really don't.”
“It's really tasty.”
“But I'm lactose intolerant.” he said. “I don’t want to risk it.”
            '''
        ).lines

        speech = rflatten([l.get_speech() for l in lines if l.get_speech() != []])

        self.assertEqual(
            [s.serialize() for s in speech],
            [
                {'text': 'Want some cheese ?', 'speaker': {'name': 'Mike', 'gender': 'male'}, 'inflection': 'asked'},
                {'text': 'I do not know .', 'speaker': {'name': 'Bob', 'gender': 'male'}, 'inflection': None},
                {'text': 'I really do not .', 'speaker': {'name': 'Bob', 'gender': 'male'}, 'inflection': 'whispered'},
                {'text': "It is really tasty .", 'speaker': {'name': '', 'gender': None}, 'inflection': None},
                {'text': 'But I am lactose intolerant .', 'speaker': {'name': 'he', 'gender': 'male'}, 'inflection': 'said'},
                {'text': 'I do not want to risk it .', 'speaker': {'name': 'he', 'gender': 'male'}, 'inflection': None}
            ]
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
        for assignment in self.ALICE.assignments:
            if 'alice' in assignment[0].text.lower():
                alice_assignments.append(assignment[2].text)
        # First assignment in the book
        self.assertTrue(
            alice_assignments[0].startswith('beginning to get very tired of sitting by her sister')
        )

    def test_alice_speech(self):
        speech_objects = self.ALICE.get_speech_by_people([Person(name='Alice')])
        
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
        self.assertEqual(
            TextBody(content='"').lang,
            'unknown'
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

    def test_wordy_profanity(self):
        self.assertEqual(
            TextBody(content='eat my ass').get_profanity_score(),
            10000
        )

    def test_contains_not_contains_profanity(self):
        # cause 'twat'
        self.assertEqual(
            TextBody(content='A wristwatch tells time').get_profanity_score(),
            0
        )

    def test_get_pre_post(self):
        pairs = self.ALICE.get_pre_post('shouted')
        self.assertEqual(pairs['pre'], ['and', 'soldiers', 'the queen'])
        self.assertEqual(pairs['post'], ['out', 'the queen', 'in', 'the queen', 'alice', 'the queen', 'the queen', 'the gryphon', 'at'])

        pairs = self.ALICE.get_pre_post('shouted', simple=True)
        self.assertEqual(pairs['pre'], ['and', 'soldiers', 'Queen'])  # warning, cause other split would give ” so would be removed
        self.assertEqual(pairs['post'], ['out', 'the', 'in', 'the', 'Alice', 'the', 'the', 'the', 'at'])

    def test_has_content(self):
        self.assertFalse(TextBody(content='').has_content)
        self.assertTrue(TextBody(content='a').has_content)

    def test_count_usage(self):
        self.assertEqual(
            TextBody(content='One two three four three two one').count_usage('one'),
            1
        )
        self.assertEqual(
            TextBody(content='One two three four three two one').count_usage('One two'),
            0
        )

        self.assertEqual(
            TextBody(content='One two three four three two one').count_usage(['two', 'One']),
            3
        )
        self.assertEqual(
            dict(TextBody(content='One two three four three two one').count_usage(['two', 'One'], split_multi=True)),
            {'One': 1, 'two': 2}
        )

        #split_multi=False, nosplit=False

#class TestTheQuickBrownFix(TestCase):
#
#    def test_brown_fox_things(self):
#        lazy_dog = TextBody(
#            content='The quick brown fox jumps over the lazy dog'
#        )
#        self.assertEqual([p.name for p in lazy_dog.things], ['fast brown fox', 'lazy dog'])
