
from unittest import TestCase
import mock

import glob
import os

from mauve.models.text import Sentence, Segment
from mauve.models.books.book import Book
from mauve.models.books.review import Reviews, Review
from mauve.models.books.tag import Tags, Tag
from mauve import constants

from mauve.models.speech import Speech, extract_speech


class TestSynonym(TestCase):

    def test_synonym(self):

        speech = extract_speech(Sentence('"Shut up" he said'))
        self.assertEqual(speech.text, 'Shut up')
        self.assertEqual(speech.inflection, 'said')
        self.assertEqual(speech.speaker, 'he')
