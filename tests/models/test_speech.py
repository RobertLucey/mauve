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
from mauve.utils import quote_aware_sent_tokenize, flatten

from mauve.models.speech import Speech, extract_speech


class TestSpeech(TestCase):

    def test_speech_speech_before(self):
        speech = extract_speech(Sentence('"Shut up" he said'))[0]
        self.assertEqual(speech.text.strip(), 'Shut up')
        self.assertEqual(speech.inflection.strip(), 'said')
        self.assertEqual(speech.speaker.name.strip(), 'he')

    def test_speech_speech_after(self):
        speech = extract_speech(Sentence('He said "Shut up"'))[0]
        self.assertEqual(speech.text.strip(), 'Shut up')
        self.assertEqual(speech.inflection.strip(), 'said')
        self.assertEqual(speech.speaker.name.strip(), 'he')

    def test_extra_speech_after(self):
        speech = extract_speech(Sentence('And then Robert exclaimed "Shut up"'))[0]
        self.assertEqual(speech.text.strip(), 'Shut up')
        self.assertEqual(speech.inflection.strip(), 'exclaimed')
        self.assertEqual(speech.speaker.name.strip(), 'Robert')

    def test_extra_speech_before(self):
        speech = extract_speech(Sentence('"Shut up" Robert exclaimed to Mikey'))[0]
        self.assertEqual(speech.text.strip(), 'Shut up')
        self.assertEqual(speech.inflection.strip(), 'exclaimed')
        self.assertEqual(speech.speaker.name.strip(), 'Robert')


    def test_real_text(self):
        content = '''
Hallward painted away with that marvellous bold touch of his, that had the true refinement and perfect delicacy that in art, at any rate comes only from strength.  He was unconscious of the silence.

"Basil, I am tired of standing," cried Dorian Gray suddenly.  "I must go out and sit in the garden.  The air is stifling here."

"My dear fellow, I am so sorry.  When I am painting, I can't think of anything else.  But you never sat better.  You were perfectly still.  And I have caught the effect I wanted--the half-parted lips and the bright look in the eyes.  I don't know what Harry has been saying to you, but he has certainly made you have the most wonderful expression.  I suppose he has been paying you compliments.  You mustn't believe a word that he says."
        '''

        sentences = [Sentence(s) for s in quote_aware_sent_tokenize(content)]

        speech_parts = flatten([s.speech for s in sentences if s.speech])

        self.assertEquals(
            [s.serialize() for s in speech_parts if s],
            [
                {'text': 'Basil , I am tired of standing ,', 'speaker': {'name': 'Dorian Gray', 'gender': 'male'}, 'inflection': 'cried'},
                {'text': 'I must go out and sit in the garden . The air is stifling here .', 'speaker': {'name': '', 'gender': None}, 'inflection': None},
                {'text': "My dear fellow , I am so sorry . When I am painting , I ca n't think of anything else . But you never sat better . You were perfectly calm . And I have caught the put I wanted -- the half-parted lips and the interesting look in the eyes . I do n't know what Harry has been saying to you , but he has certainly made you have the most good expression . I suppose he has been paying you compliments . You must n't think a word that he says .", 'speaker': {'name': '', 'gender': None}, 'inflection': None}
            ]
        )

    def test_multiple_speech(self):
        content = '''
“If you didn’t sign it,” said the King, “that only makes the matter worse. You _must_ have meant some mischief, or else you’d have signed your name like an honest man.”
'''
        sentences = [Sentence(s) for s in quote_aware_sent_tokenize(content)]

        speech_parts = flatten([s.speech for s in sentences if s.speech])

        self.assertEqual(
            [s.serialize() for s in speech_parts if s],
            [
                {'text': 'If you didn ’ t mark it ,', 'speaker': {'name': 'King', 'gender': 'male'}, 'inflection': 'said'},
                {'text': 'that only makes the matter worse . You  must  have meant some mischief , or else you ’ d have signed your name love an right man .', 'speaker': {'name': 'King', 'gender': 'male'}, 'inflection': 'said'}
            ]
        )
