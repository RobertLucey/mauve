import time
from collections import deque


class WPS:

    def __init__(self, past_seconds=5 * 60, print_rate=None):
        """

        :kwarg past_seconds: How long in the past to judge wps from
        :kwarg print_rate: The tick at which to print the wps
        """
        self.data = deque([])
        self.past_seconds = past_seconds
        self.print_rate = print_rate
        self.count = 0

    def update(self):
        """
        To be called at every word processed
        """
        self.clean_queue()
        self.data.appendleft(time.monotonic())

        if self.print_rate is not None:
            self.count += 1
            if self.count % self.print_rate == 0:
                print(round(self.wps(), 2))

    def wps(self):
        """
        Get the wps

        :return: The number of words processed per second
        :rtype: float
        """
        try:
            time_from_queue = self.data[0] - self.data[-1]
            return len(self.data) / time_from_queue
        except ZeroDivisionError:
            return 0.

    def clean_queue(self):
        """
        Remove old data from the queue so that we only look
        at the self.past_seconds seconds for getting the wps
        """
        if self.data != deque([]):
            while (time.monotonic() - self.data[-1]) > self.past_seconds:
                self.data.pop()
