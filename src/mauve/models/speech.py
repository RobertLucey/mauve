from typing import Iterable, Mapping, Any

from mauve.constants import (
    SPEECH_QUOTES,
    SPEECH_WORDS,
    SPEAKERS,
    EXTENDED_PUNCTUATION
)
from mauve.models.person import Person


class Speech:

    def __init__(
        self,
        text=None,
        segments=None,
        speaker=None,
        inflection=None
    ):
        '''

        :kwarg text: The text of the speech
        :kwarg segments: The segments of the speech.
            Can prob replace text with this parsed
        :kwarg speaker: the identifier of the speaker
        :kwarg inflection: said / exclaimed / however someone said the speech.
            Should rename to something verby
        '''
        self.segments = segments
        self._text = text
        self.speaker = speaker
        self._inflection = inflection

    @property
    def sentences(self):
        # the sentences of the text since there can be multiple
        # sentences from quote_aware_sent_tokenize
        raise NotImplementedError()

    @property
    def text(self) -> str:
        if self._text is not None:
            return self._text
        return ' '.join([s.text for s in self.segments]).strip()

    @property
    def inflection(self) -> str:
        inflection = None
        if self._inflection:
            inflection = self._inflection
        return inflection

    def serialize(self) -> Mapping[str, Any]:
        return {
            'text': self.text,
            'speaker': self.speaker.serialize(),
            'inflection': self.inflection,
        }


def extract_speech(sentence) -> Iterable[Speech]:
    """

    :param sentence:
    :return: List of Speech objects
    :rtype: list
    """

    if not any([quotemark in sentence.text for quotemark in SPEECH_QUOTES]):
        return []

    speech_parts = []

    within = False
    broken_idx = -1
    start_speech_idx = -1

    # Some books do:
    # He said 'Yah yah yah.' And what did that mean?

    # said the cat, the cat said. We should shuffle and use only one I guess for handiness sake?

    num_breaks = 0
    # starting idx would be handy for he said "shut up"
    for idx, segment in enumerate(sentence.segments):
        if segment.text in SPEECH_QUOTES and within:
            num_breaks += 1
            within = False
            broken_idx = idx
            if num_breaks % 2 == 1:
                speech_parts.append((start_speech_idx, broken_idx))

        if segment.text in SPEECH_QUOTES and not within:
            start_speech_idx = idx
            within = True

    if not speech_parts:
        return []

    speech_items = []

    for start_idx, end_idx in speech_parts:
        text = sentence.segments[start_idx+1:end_idx]
        after_speech = sentence.segments[end_idx + 1:end_idx + 4]
        pre_speech = sentence.segments[max(start_idx - 4, 0):max(start_idx, 0)]

        inflection = None
        speaker = None

        for interesting_part in [after_speech, pre_speech]:
            interesting_part = [c for c in interesting_part if c.text not in EXTENDED_PUNCTUATION]
            set_inflection = False
            inflection_intersection = set(
                [
                    f.text.lower() for f in interesting_part
                ]
            ).intersection(SPEECH_WORDS)
            if inflection_intersection != set():
                # handle if multiple
                inflection = list(inflection_intersection)[0]
                set_inflection = True

            if inflection is not None:
                try:
                    interesting_part.remove(inflection)
                except:
                    pass

            speaker_intersection = set(
                [
                    f.text.lower() for f in interesting_part
                ]
            ).intersection(SPEAKERS)
            if speaker_intersection != set():
                # handle if multiple
                # also check for names, not just pronouns
                speaker = list(speaker_intersection)[0]

            for i in interesting_part:
                if i.is_person:
                    speaker = i.text

            # If has inflected more likely
            # also a good sign if there's few words and one of them is the
            if speaker is None and set_inflection:
                if len(interesting_part) < 3:
                    speaker = ' '.join([i.text for i in interesting_part])

        # if we have a name, that's a better speaker
        speech_items.append(
            Speech(
                segments=text,
                speaker=Person(name=speaker),
                inflection=inflection
            )
        )

    return speech_items
