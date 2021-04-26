from unittest import TestCase

from mauve.preprocess.number_convert import convert_numbers


class TestNumberConvert(TestCase):

    def test_number_convert_no_numbers(self):
        self.assertEqual(convert_numbers('blah blah'), 'blah blah')

    def test_number_convert_only_numbers(self):
        self.assertEqual(convert_numbers('zero'), '0')
        self.assertEqual(convert_numbers('fifty-three'), '53')
        self.assertEqual(convert_numbers('fifty three'), '53')

    def test_number_convert_only_numbers_at_end(self):
        self.assertEqual(convert_numbers('something zero'), 'something 0')
        self.assertEqual(convert_numbers('something fifty three'), 'something 53')
        self.assertEqual(convert_numbers('something fifty-three'), 'something 53')
        self.assertEqual(convert_numbers('something one million and fifty-three'), 'something 1000053')

    def test_number_convert_only_numbers_at_start(self):
        self.assertEqual(convert_numbers('zero something'), '0 something')
        self.assertEqual(convert_numbers('fifty three something'), '53 something')
        self.assertEqual(convert_numbers('one million and fifty three something'), '1000053 something')

    def test_number_convert_numbers_in_middle(self):
        self.assertEqual(
            convert_numbers('Something fifty three blah blah'),
            'Something 53 blah blah'
        )

    def test_number_convert_numbers_everywhere(self):
        self.assertEqual(
            convert_numbers('zero Something fifty three blah blah one'),
            '0 Something 53 blah blah 1'
        )

    def test_combination(self):
        # could convert all numbers to words and then back? boo though
        self.assertEqual(
            convert_numbers('about 600 million or so'),
            'about 600000000 or so'
        )

    def test_monitary_combination(self):
        self.assertEqual(
            convert_numbers('$2 million'),
            '$2000000'
        )

    def test_colloquial(self):
        self.assertEqual(
            convert_numbers('two-fifty'),
            '250'
        )
        self.assertEqual(
            convert_numbers('two-fifty-one'),
            '251'
        )

    def test_year(self):
        self.assertEqual(
            convert_numbers('nineteen-fifty-five'),
            '1955'
        )
        self.assertEqual(
            convert_numbers('nineteen hundred and two'),
            '1902'
        )

    def test_ordinal(self):
        self.assertEqual(
            convert_numbers('fifty-first'),
            '51'
        )

    def test_implied(self):
        self.assertEqual(
            convert_numbers('a hundred and fifty'),
            'a 150'
        )

        self.assertEqual(
            convert_numbers('hundred and fifty'),
            '150'
        )

    def test_word(self):
        self.assertEqual(
            convert_numbers('nine billion and nine thousand'),
            '9000009000'
        )
        self.assertEqual(
            convert_numbers('nine billion nine thousand'),
            '9000009000'
        )
        self.assertEqual(
            convert_numbers('nine million three hundred'),
            '9000300'
        )
        self.assertEqual(
            convert_numbers('seven million, eight hundred, and sixty three thousand, two hundred, and fifty four'),
            '7863254'
        )
        self.assertEqual(
            convert_numbers('one billion two hundred seventy four million'),
            '1274000000'
        )
        self.assertEqual(
            convert_numbers('want a million?'),
            'want a 1000000 ?'
        )

    def test_inside_word(self):
        self.assertEqual(
            convert_numbers('are you attending the show?'),
            'are you attending the show?'
        )

    def test_unordered_ordinal(self):
        self.assertEqual(
            convert_numbers('In the first twenty years'),
            'In the first 20 years'
        )

    def test_dash_joined(self):
        self.assertEqual(
            convert_numbers('blah blah fifteen-year-old blah'),
            'blah blah 15 year old blah'
        )

        self.assertEqual(
            convert_numbers('blah blah twenty-five-year-old blah'),
            'blah blah 25 year old blah'
        )

