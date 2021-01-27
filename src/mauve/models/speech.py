import re

from mauve.utils import (
    lower,
    previous_current_next
)

from mauve.models.deptree import DepTree, DepNode


class Speech():

    def __init__(self, text=None, segments=None, speaker=None):
        self.segments = segments
        self._text = text
        self.speaker = speaker

    @property
    def text(self):
        if self._text is not None:
            return self._text
        return ' '.join([s.text for s in self.segments])

    @property
    def inflection(self):
        return  # Tom exclaimed / whispered

    def serialize(self):
        return {
            'text': self.text,
            'speaker': self.speaker,
            'inflection': self.inflection,
        }


def extract_speech(sentence, use_deptree=True):

    quotes = ['\'', '`', '‘', '"', '``', '\'\'']

    within = False
    within_section = []
    broken_idx = -1

    # Some books do:
    # He said 'Yah yah yah.' And what did that mean?

    # said the cat, the cat said. We should shuffle and use only one I guess for handiness sake?

    # starting idx would be handy for he said "shut up"
    for idx, s in enumerate(sentence.segments):

        if s.text in quotes and within:
            within = False
            broken_idx = idx
            break  # allow for multiple once one works

        if within:
            within_section.append(s)

        if s.text in quotes and not within:
            within = True

    print([s.text for s in sentence.segments[broken_idx + 1:]])

    return Speech(
        segments=within_section,
        speaker=None
    )
