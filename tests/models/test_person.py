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
