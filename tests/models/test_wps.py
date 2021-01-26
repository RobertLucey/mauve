from time import sleep
from unittest import TestCase

from mauve.wps import WPS


class TestWPS(TestCase):

    def test_wps(self):
        wps = WPS()
        for _ in range(100):
            sleep(0.05)
            wps.update()
        self.assertTrue(abs(wps.wps() - 20.0) < 0.2)

        wps = WPS(past_seconds=1)
        for _ in range(30):
            sleep(0.05)
            wps.update()
        self.assertTrue(len(wps.data) == 20)
