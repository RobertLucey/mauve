import time
from collections import deque


class WPS():

    def __init__(self, past_seconds=5 * 60, print_rate=None):
        self.data = deque([])
        self.past_seconds = past_seconds
        self.print_rate = print_rate
        self.count = 0

    def update(self):
        self.clean_queue()
        self.data.appendleft(time.monotonic())

        if self.print_rate is not None:
            self.count += 1
            if self.count % self.print_rate == 0:
                print(round(self.wps(), 2))

    def wps(self):
        try:
            time_from_queue = self.data[0] - self.data[-1]
            return len(self.data) / time_from_queue
        except ZeroDivisionError:
            return 0

    def clean_queue(self):
        if self.data == deque([]):
            return

        while (time.monotonic() - self.data[-1]) > self.past_seconds:
            self.data.pop()
