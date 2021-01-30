from unittest import TestCase
import mock

import glob
import os

from mauve.models.comparitor import Comparitor


class TestComparitor(TestCase):

    def test_tense_sort(self):

        _is = Comparitor('is')
        was = Comparitor('was')
        will_be = Comparitor('will_be')
        could_be = Comparitor('could___be')

        self.assertEqual(
            sorted([could_be, will_be, _is, was]),
            [was, could_be, _is, will_be]
        )
