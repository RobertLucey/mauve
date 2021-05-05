from typing import (
    Mapping,
    Any,
    Iterable
)
import logging

from mauve.models.sentence import Sentence
from mauve.constants.names import NAMES
from mauve.models.generic import (
    GenericObject,
    GenericObjects
)
from mauve.utils import (
    rflatten,
    quote_aware_sent_tokenize,
)

from mauve.models.person import Person
from mauve.models.speech import extract_speech

# Do text extraction by line since by sentence cuts ends off

logger = logging.getLogger('mauve')


class Line(GenericObject):

    def __init__(self, text, **kwargs):
        if '\n' in text:
            logger.warning('Line contains a newline: %s', text)

        self.text = text.strip()
        self.line_no = kwargs.get('line_no', None)

    def get_speech(self) -> Iterable:

        def assign_best_name(speech_parts: Iterable) -> Iterable:
            # FIXME: what if a line has multiple speakers? Does this happen somewhere?

            is_multi_speaker = len(
                set(
                    [
                        item.speaker.name for item in speech_parts if item.speaker.name and item.speaker.name[0].isupper()
                    ]
                )
            ) > 1

            if is_multi_speaker:
                return speech_parts

            best_name = None
            for speech_item in speech_parts:
                if best_name is None and speech_item.speaker.name != '':
                    best_name = speech_item.speaker.name
                elif speech_item.speaker.name != '':
                    if speech_item.speaker.name in NAMES and best_name not in NAMES:
                        best_name = speech_item.speaker.name

            for speech_item in speech_parts:
                speech_item.speaker = Person(name=best_name)

            return speech_parts

        # can probably use extract speech from here without copy paste
        # by using quote_aware_sent_tokenize

        sentences_text = quote_aware_sent_tokenize(self.text)
        speech_parts = [extract_speech(Sentence(sentence)) for sentence in sentences_text]
        speech_parts = assign_best_name(rflatten(speech_parts))

        return speech_parts

    def serialize(self) -> Mapping[str, Any]:
        return {
            'text': self.text,
            'line_no': self.line_no,
        }


class Lines(GenericObjects):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('child_class', Line)
        super(Lines, self).__init__(*args, **kwargs)

    def get_speech(self):
        pass
