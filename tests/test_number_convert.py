from unittest import TestCase

from mauve.number_convert import convert_numbers


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
            convert_numbers('60 million'),
            '60000000'
        )

    def test_monitary_combination(self):
        self.assertEqual(
            convert_numbers('$2 million'),
            '$2000000'
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
