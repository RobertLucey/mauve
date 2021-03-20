from unittest import TestCase
import mock

from mauve.bin.scrape_author_nationality import clean_person, get_wikipedia_person_by_href


class TestScrapeAuthorNationality(TestCase):

    '''
  
--def clean_person(person):
  
--    def parse_birth_year(birth_year):
          if birth_year is None:
              return None
          return birth_year if birth_year < 2020 and birth_year > 1000 else None
  
--    def parse_nationality(nationality):
--        # TODO: clean dual citizen
          return EXTRA_COUNTRIES_MAP.get(nationality, nationality)
  
      return {
          'born': parse_birth_year(person['born']),
          'nationality': parse_nationality(person['nationality'])
      }

    '''

    def test_clean_person(self):
        self.assertEqual(
            clean_person(
                {'born': None, 'nationality': None}
            ),
            {'born': None, 'nationality': None}
        )

        self.assertEqual(
            clean_person(
                {'born': 1980, 'nationality': None}
            ),
            {'born': 1980, 'nationality': None}
        )

        self.assertEqual(
            clean_person(
                {'born': None, 'nationality': 'Ireland'}
            ),
            {'born': None, 'nationality': 'Ireland'}
        )

        self.assertEqual(
            clean_person(
                {'born': 1980, 'nationality': 'Ireland'}
            ),
            {'born': 1980, 'nationality': 'Ireland'}
        )

        self.assertEqual(
            clean_person(
                {'born': 1980, 'nationality': 'Irish'}
            ),
            {'born': 1980, 'nationality': 'Ireland'}
        )

    def test_get_wikipedia_person(self):
        self.assertEqual(
            get_wikipedia_person_by_href('/wiki/Stephen_King'),
            {'born': 1947, 'nationality': 'U.S.'}
        )

        self.assertEqual(
            get_wikipedia_person_by_href('/wiki/Cloud'),
            {'born': None, 'nationality': None}
        )

        # TODO: Find and try out tough ones
