from unittest import TestCase
import mock

import glob
import os

from mauve.models.text import TextBody
from mauve import constants


class TestUsage(TestCase):

    def test_usage(self):
        """
        Just make sure the usage in the readme still works
        """
        text = TextBody(content='“You are not attending!” said the Mouse to Alice severely. “What are you thinking of?”')
        self.assertEqual(
            text.people.serialize(),
            [{'name': 'Mouse', 'gender': None}, {'name': 'Alice', 'gender': 'female'}]
        )
        self.assertEqual(
            text.get_speech_by_people()['Mouse'][0].serialize(),
            {'text': 'You are not attending !', 'speaker': {'name': 'Mouse', 'gender': None}, 'inflection': 'said'}
        )

        assignment = text.assignments[0]
        self.assertEqual(
            [a.text for a in assignment],
            ['You', 'are', 'not attending']
        )

        self.assertEqual(
            TextBody(content='London is the capital of Paris, and Paris is the capital of Rome').get_assignments_by('Paris'),
            ['the capital of Rome']
        )

        text = TextBody(content='“Bad no this sucks” said the Mouse to Alice. Alice replied, “Happy Love”')
        self.assertEqual(
            text.get_sentiment_by_people(),
            {'Mouse': {'neg': 0.647, 'neu': 0.114, 'pos': 0.24, 'compound': -0.5559}, 'Alice': {'neg': 0.0, 'neu': 0.0, 'pos': 1.0, 'compound': 0.836}}
        )

        self.assertEqual(
            TextBody(content='“This is a load of ass!” said the Mouse').get_profanity_score(),
            1111.111111111111
        )

        self.assertEqual(
            TextBody(content='“This is a load of ass!” said the Mouse to Alice severely. “That\'s rude my dude” whispered Alice').get_profanity_by_people(),
            {'Mouse': 1666.6666666666667, 'Alice': 0}
        )
