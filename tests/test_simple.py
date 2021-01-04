from unittest import TestCase

import mauve


class TestSimple(TestCase):

    def test_simple(self):
        self.assertEqual(
            1 + 1,
            2
        )
