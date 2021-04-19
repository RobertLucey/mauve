from unittest import TestCase

from mauve.number_convert import convert_numbers


class TestNumberConvert(TestCase):

    def test_number_convert_no_numbers(self):
        self.assertEqual(convert_numbers('blah blah'), 'blah blah')

    def test_number_convert_only_numbers(self):
        self.assertEqual(convert_numbers('zero'), ' 0')
        self.assertEqual(convert_numbers('fifty-three'), ' 53')
        self.assertEqual(convert_numbers('fifty three'), ' 53')

    def test_number_convert_only_numbers_at_end(self):
        self.assertEqual(convert_numbers('something zero'), 'something 0')

    def test_number_convert_only_numbers_at_start(self):
        self.assertEqual(convert_numbers('zero something'), ' 0  something')

    def test_number_convert_numbers_in_middle(self):
        self.assertEqual(
            convert_numbers('Something thirty four blah blah'),
            'Something 34 blah blah'
        )

    def test_number_convert_numbers_everywhere(self):
        self.assertEqual(
            convert_numbers('zero Something thirty four blah blah one'),
            '0 Something 34 blah blah 1'
        )
