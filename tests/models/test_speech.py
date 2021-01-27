
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

from mauve.models.speech import Speech, extract_speech


class TestSynonym(TestCase):

    def test_synonym(self):

        speech = extract_speech(Sentence('"Shut up" he said'))
        self.assertEqual(speech.text.strip(), 'Shut up')
        self.assertEqual(speech.inflection.strip(), 'said')
        self.assertEqual(speech.speaker.strip(), 'he')

        speech = extract_speech(Sentence('He said "Shut up"'))
        self.assertEqual(speech.text.strip(), 'Shut up')
        self.assertEqual(speech.inflection.strip(), 'said')
        self.assertEqual(speech.speaker.strip(), 'he')

        speech = extract_speech(Sentence('And then Robert exclaimed "Shut up"'))
        self.assertEqual(speech.text.strip(), 'Shut up')
        self.assertEqual(speech.inflection.strip(), 'exclaimed')
        self.assertEqual(speech.speaker.strip(), 'Robert')

        speech = extract_speech(Sentence('"Shut up" Robert exclaimed to Mikey'))
        self.assertEqual(speech.text.strip(), 'Shut up')
        self.assertEqual(speech.inflection.strip(), 'exclaimed')
        self.assertEqual(speech.speaker.strip(), 'Robert')
