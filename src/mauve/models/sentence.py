from cached_property import cached_property
import logging
from typing import Iterable, Any, Mapping

import textacy.ke
import nltk

from mauve import SYNONYM
from mauve.structure.assignment import extract_assignments
from mauve.structure.conditional import extract_conditionals
from mauve.models.speech import extract_speech
from mauve.utils import (
    make_spacy_doc,
    replace_sub,
    get_en_core_web_sm
)
from mauve.preprocess.phrases import replace_phrases
from mauve.models.deptree import (
    DepTree,
    DepNode
)
from mauve.models.person import extract_people
from mauve.models.segment import Segment

logger = logging.getLogger('mauve')


class Sentence:

    def __init__(self, text: str):
        self.text = text

    def serialize(self) -> Mapping[str, Any]:
        return {
            'text': self.text,
            'people': self.people,
            'is_question': self.is_question
        }

    @property
    def deptree(self) -> DepTree:
        doc = get_en_core_web_sm(self.get_unsplit_text)

        return DepTree([
            DepNode(
                token.text,
                token.dep_,
                token.head.text,
                token.head.pos_,
                [child for child in token.children],
                token.idx
            ) for token in doc
        ])

    @cached_property
    def people(self):
        return extract_people(self)

    @property
    def is_question(self) -> bool:
        try:
            return self.text.strip()[-1] == '?'
        except IndexError:
            return False

    @staticmethod
    def preprocess_text(text: str) -> str:
        return ' '.join([SYNONYM.get_word(t.replace(' ', '_')) for t in nltk.word_tokenize(text)])

    @cached_property
    def get_unsplit_text(self) -> str:
        self.text = self.preprocess_text(replace_phrases(self.text))

        sentence = get_en_core_web_sm(self.text)
        mod_text = self.text
        mapping = {}

        for entity in sentence.ents:
            if '_' in entity.text:
                # This is one of ours, messes things up often
                continue
            to_put = entity.text.replace(' ', '___')
            mod_text = mod_text.replace(entity.text, to_put)
            mapping[to_put] = entity.label_

        try:
            doc = make_spacy_doc(mod_text)
        except Exception as ex:
            logger.warning('Could not create spacy doc: %s', ex)
        else:
            textphrases = [
                k[0] for k in textacy.ke.textrank(
                    doc,
                    normalize='lemma',
                    topn=10
                ) if ' ' in k[0] or '_' in k[0]  # only really care about multi word phrases
            ]

            for textphrase in textphrases:
                to_put = textphrase.replace(' ', '___')
                mod_text = mod_text.replace(textphrase, to_put)
                mapping[textphrase] = 'SOMETHING'

        return mod_text

    @cached_property
    def base_segments(self) -> Iterable[Segment]:
        self.text = self.preprocess_text(self.text)

        sentence = get_en_core_web_sm(self.text)
        mod_text = self.text
        mapping = {}

        for entity in sentence.ents:
            to_put = entity.text.replace(' ', '___')
            mod_text = mod_text.replace(entity.text, to_put)
            mapping[to_put] = entity.label_

        try:
            doc = make_spacy_doc(mod_text)
        except Exception as ex:
            logger.warning('Could not create spacy doc: %s', ex)
        else:
            textphrases = [
                k[0] for k in textacy.ke.textrank(
                    doc,
                    normalize='lemma',
                    topn=10
                ) if ' ' in k[0] or '_' in k[0]  # only really care about multi word phrases
            ]

            for textphrase in textphrases:
                to_put = textphrase.replace(' ', '___')
                mod_text = mod_text.replace(textphrase, to_put)
                mapping[textphrase] = 'SOMETHING'

        return [
            Segment(
                text,
                tag=mapping.get(text, None)
            ) for text in nltk.word_tokenize(mod_text)
        ]

    @cached_property
    def segments(self) -> Iterable[Segment]:
        segments = self.base_segments
        people = self.people

        for person in people:
            segments = replace_sub(  # keep the object
                segments,
                [Segment(p) for p in person.dirty_name.split(' ')],
                [Segment(person.dirty_name, tag='PERSON')]
            )
            segments = replace_sub(
                segments,
                ['the'] + [Segment(p) for p in person.dirty_name.split(' ')],
                [Segment('the ' + person.dirty_name, tag='PERSON')]
            )
            segments = replace_sub(
                segments,
                ['a'] + [Segment(p) for p in person.dirty_name.split(' ')],
                [Segment('a ' + person.dirty_name, tag='PERSON')]
            )

        return segments

    @cached_property
    def assignments(self):
        return extract_assignments(self)

    @cached_property
    def speech(self) -> Iterable:
        return extract_speech(self)

    @property
    def lvr(self) -> Iterable:
        assignments = extract_assignments(self)
        conditionals = extract_conditionals(self)
        return assignments + conditionals
