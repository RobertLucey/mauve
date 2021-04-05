from unittest import TestCase
from mauve.contractions import replace_contractions


class TestIdioms(TestCase):

    def test_replace_contractions(self):
        self.assertEqual(
            replace_contractions('it\'s I\'m I am'),
            'it is I am I am'
        )
