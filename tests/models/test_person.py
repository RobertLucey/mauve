from unittest import TestCase
import mock

import glob
import os

from mauve.models.person import Person


class TestPerson(TestCase):

    def test_gender(self):

        test_map = {
            'Robert Lucey': 'male',
            'Robert': 'male',
            'Mr Lucey': 'male',
            'Mrs. Lucey': 'female',
            'Lady Manlyname': 'female'
        }

        for name, gender in test_map.items():
            self.assertEquals(
                Person(name=name).gender,
                gender,
                name
            )

    def test_name_parse(self):

        test_map = {
            'the great bob': 'great bob',
            'chapter two': '',
        }

        for name, gender in test_map.items():
            self.assertEquals(
                Person(name=name).name,
                gender,
                name
            )
