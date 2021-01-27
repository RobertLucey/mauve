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

    speech_words = ['said', 'says', 'exclaimed', 'whispered', 'wrote', 'continued', 'told', 'shouted', 'called', 'recalled', 'explained', 'admitted', 'remarked', 'bellowed', 'shrieked', 'told', 'ask', 'asked', 'confided', 'fulminated', 'mused', 'rejoined', 'cried', 'panted', 'continued', 'ejaculated', 'replied', 'interrupted', 'remarked', 'declared', 'queried', 'repeated', 'added', 'lied', 'insisted', 'answered']
    speakers = ['he', 'they', 'she', 'I', 'we']

    quotes = ['`', '‘', '"', '``', '\'\'']

    within = False
    within_section = []
    broken_idx = -1
    start_speech_idx = -1

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
            print('app: "%s"' % (s.text))
            within_section.append(s)

        if s.text in quotes and not within:
            start_speech_idx = idx
            within = True

    after_speech = sentence.segments[broken_idx + 1:broken_idx + 4]
    pre_speech = sentence.segments[max(start_speech_idx - 4, 0):max(start_speech_idx, 0)]

    inflection = None
    speaker = None

    for interesting_part in [after_speech, pre_speech]:

        inflection_intersection = set([f.text.lower() for f in interesting_part]).intersection(set(speech_words))
        if inflection_intersection != set():
            # handle if multiple
            inflection = list(inflection_intersection)[0]

        speaker_intersection = set([f.text.lower() for f in interesting_part]).intersection(set(speakers))
        if speaker_intersection != set():
            # handle if multiple
            # also check for names, not just pronouns
            speaker = list(speaker_intersection)[0]

        for i in interesting_part:
            if i.tag == 'PERSON':
                speaker = i.text

        # if we have a name, that's a better speaker

    return Speech(
        segments=within_section,
        speaker=speaker,
        inflection=inflection
    )
