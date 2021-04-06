from cached_property import cached_property

import textacy.ke
import nltk

from mauve.models.sentence import Sentence

from mauve.constants import (
    SPEECH_QUOTES,
    EXTENDED_PUNCTUATION,
    SPEECH_WORDS,
    SPEAKERS
)
from mauve.structure.assignment import extract_assignments
from mauve.structure.conditional import extract_conditionals
from mauve.models.speech import extract_speech

from mauve.models.generic import GenericObject, GenericObjects
from mauve.utils import (
    rflatten,
    replace_sub,
    get_en_core_web_sm,
    replace_phrases,
    quote_aware_sent_tokenize,
)

from mauve.models.deptree import DepTree, DepNode
from mauve.models.person import Person
from mauve.models.segment import Segment
from mauve.models.speech import Speech, extract_speech
from mauve import SYNONYM

# Do text extraction by line since by sentence cuts ends off

class Line(GenericObject):

    def __init__(self, text, **kwargs):
        self.text = text.strip()
        self.line_no = kwargs.get('line_no', None)

    def get_speech(self):

        def assign_best_name(speech_parts):
            # FIXME: what if a line has multiple speakers? Does this happen somewhere?

            is_multi_speaker = len(set([speech_item.speaker.name for speech_item in speech_parts if speech_item.speaker.name and speech_item.speaker.name[0].isupper()])) > 1

            if is_multi_speaker:
                return speech_parts

            best_name = None
            for speech_item in speech_parts:
                if best_name is None and speech_item.speaker.name != '':
                    best_name = speech_item.speaker.name
                elif speech_item.speaker.name != '':
                    if best_name[0].islower() and speech_item.speaker.name.isupper():
                        best_name = speech_item.speaker.name
            for speech_item in speech_parts:
                speech_item.speaker = Person(name=best_name)

            return speech_parts

        def process_speech_parts(speech_parts):
            return 


        # can probably use extract speech from here without copy paste
        # by using quote_aware_sent_tokenize

        sentences_text = quote_aware_sent_tokenize(self.text)
        speech_parts = [extract_speech(Sentence(sentence)) for sentence in sentences_text]
        speech_parts = assign_best_name(rflatten(speech_parts))

        return speech_parts


    def serialize(self):
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