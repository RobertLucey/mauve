import re

from mauve.utils import (
    lower,
    previous_current_next
)

from mauve.models.deptree import DepTree, DepNode


class Speech():

    def __init__(self, text=None, segments=None, speaker=None, inflection=None):
        self.segments = segments
        self._text = text
        self.speaker = speaker
        self._inflection = inflection

    @property
    def text(self):
        if self._text is not None:
            return self._text
        return ' '.join([s.text for s in self.segments])

    @property
    def inflection(self):
        if self._inflection:
            return self._inflection
        return  # Tom exclaimed / whispered

    def serialize(self):
        return {
            'text': self.text,
            'speaker': self.speaker,
            'inflection': self.inflection,
        }


def extract_speech(sentence, use_deptree=True):

    speech_words = ['said', 'exclaimed', 'whispered']
    speakers = ['he', 'they', 'she', 'I', 'we']

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

    after_speech = sentence.segments[broken_idx + 1:broken_idx + 4]

    inflection = None
    inflection_intersection = set([f.text for f in after_speech]).intersection(set(speech_words))
    if inflection_intersection != set():
        # handle if multiple
        inflection = list(inflection_intersection)[0]

    speaker = None
    speaker_intersection = set([f.text for f in after_speech]).intersection(set(speakers))
    if speaker_intersection != set():
        # handle if multiple
        # also check for names, not just pronouns
        speaker = list(speaker_intersection)[0]


    return Speech(
        segments=within_section,
        speaker=speaker,
        inflection=inflection
    )
