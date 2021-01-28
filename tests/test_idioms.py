from unittest import TestCase
from mauve.idioms import replace_idioms



class TestIdioms(TestCase):

    def test_replace(self):
        self.assertEqual(
            replace_idioms('It\'s about time I wrote some tests'),
            'It\'s about_time I wrote some tests'
        )

        self.assertEqual(
            replace_idioms('It\'s aBout TiMe I wrote some tests'),
            'It\'s aBout_TiMe I wrote some tests'
        )
