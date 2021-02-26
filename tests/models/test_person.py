from unittest import TestCase
import mock

import glob
import os

from mauve.models.person import (
    Person,
    People
)


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

    def test_is_trustworthy(self):
        person = Person(name='a', trustworthy=False)
        self.assertFalse(person.is_trustworthy)

        person = Person(name='a', trustworthy=False)
        for i in range(100):
            person.inc_references()
        self.assertTrue(person.is_trustworthy)

        person = Person(name='a', trustworthy=True)
        self.assertTrue(person.is_trustworthy)

    def test_is_similar_to(self):
        self.assertTrue(
            Person(name='bOB').is_similar_to(Person(name='Bob'))
        )
        self.assertTrue(
            Person(name='Mr Man').is_similar_to(Person(name='Man'))
        )
        self.assertTrue(
            Person(name='a Something').is_similar_to(Person(name='Something'))
        )
        self.assertFalse(
            Person(name='Blahlala').is_similar_to(Person(name='Blaaaaaaaa'))
        )

    def test_references(self):
        person = Person(name='a')
        self.assertEqual(person.references, 0)

        person.inc_references()
        self.assertEqual(person.references, 1)


class TestPeople(TestCase):

    def test_append(self):
        people = People()
        people.append(Person(name='a'))
        self.assertEqual(people[0].references, 1)
        people.append(Person(name='a'))
        self.assertEqual(people[0].references, 2)

    def test_remove_near_duplicates(self):
        people = People()
        people.extend([
            Person(name='Mr Man'),
            Person(name='Man'),
            Person(name='Man'),
        ])

        people.remove_near_duplicates()

        self.assertEqual(len(people), 1)
        self.assertEqual(people[0].name, 'Man')
        self.assertEqual(people[0].references, 3)

