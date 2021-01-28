
from cached_property import cached_property

import textacy.ke
import nltk

from mauve.models.assignment import Assignment, extract_assignments
from mauve.models.speech import Speech, extract_speech

from mauve.utils import (
    get_stem,
    get_lem,
    lower,
    replace_sub,
    get_wordnet_pos
)

from mauve.phrases import replace_phrases
from mauve.models.deptree import DepTree, DepNode
from mauve.models.segment import Segment
from mauve import (
    GENDER_DETECTOR,
    VADER,
    TAGGER,
    ENCORE,
    WPS,
    SYNONYM
)

from mauve.constants import (
    NAMES,
    LIKELY_PERSON_PREFIXES,
    LIKELY_WORD_TOKENS,
    ENG_WORDS,
    PROFANITY_LIST,
    SENTENCE_TERMINATORS,
    SIMPLE_TOKEN_MAP,
    ANALYSIS_VERSION
)



class Sentence():

    def __init__(self, text):
        self.text = text

    def serialize(self):
        return {
            'text': self.text,
            'people': self.people
        }

    @property
    def deptree(self):
        doc = ENCORE(self.get_unsplit_text)
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

        # Names can be chained by , and ands but we only get the last
        self.text = replace_phrases(self.text)
        people = []

        prev_was_first = False
        for segment in self.base_segments:
            if any([
                'minister for ' in segment.text.lower().replace('_', ' '),
                'minister of ' in segment.text.lower().replace('_', ' ')
            ]):
                people.append(segment.text)
            elif segment.tag == 'PERSON' or (
                segment.tag == 'dunno' and (
                    any([segment.text.lower().replace('_', ' ').startswith(prefix) for prefix in LIKELY_PERSON_PREFIXES])
                )
            ):
                people.append(segment.text)
            else:
                # do some stuff around caital letters

                if ' ' in segment.text:
                    if all([i in NAMES for i in segment.text.split(' ')]):
                        people.append(segment.text)
                        continue


                # or if already a segment and not a name see the split of ' '
                if segment.text in NAMES:
                    if not prev_was_first:
                        prev_was_first = True
                        people.append(segment.text)
                    else:
                        people[-1] += ' ' + segment.text
                else:
                    prev_was_first = False
        # also look for names
        return people

    @property
    def is_question(self):
        return self.text[-1] == '?'

    def preprocess_text(self, text):
        return ' '.join([SYNONYM.get_word(t.replace(' ', '_')) for t in nltk.word_tokenize(text)])

    @cached_property
    def get_unsplit_text(self):
        self.text = self.preprocess_text(replace_phrases(self.text))

        sentence = ENCORE(self.text)

        mod_text = self.text
        mapping = {}

        for e in sentence.ents:
            to_put = e.text.replace(' ', '___')
            mod_text = mod_text.replace(e.text, to_put)
            mapping[to_put] = e.label_

        try:
            doc = textacy.make_spacy_doc(mod_text)
        except Exception as ex:
            print(ex)
        else:
            things = [
                k[0] for k in textacy.ke.textrank(
                    doc,
                    normalize='lemma',
                    topn=10
                ) if ' ' in k[0] or '_' in k[0] # only really care about multi word phrases
            ]

            for t in things:
                to_put = t.replace(' ', '___')
                mod_text = mod_text.replace(t, to_put)
                mapping[t] = 'SOMETHING'
        return mod_text

    @cached_property
    def base_segments(self):
        self.text = self.preprocess_text(self.text)

        sentence = ENCORE(self.text)

        mod_text = self.text
        mapping = {}

        for e in sentence.ents:
            to_put = e.text.replace(' ', '___')
            mod_text = mod_text.replace(e.text, to_put)
            mapping[to_put] = e.label_

        try:
            doc = textacy.make_spacy_doc(mod_text)
        except Exception as ex:
            print(ex)
        else:
            things = [
                k[0] for k in textacy.ke.textrank(
                    doc,
                    normalize='lemma',
                    topn=10
                ) if ' ' in k[0] or '_' in k[0] # only really care about multi word phrases
            ]

            for t in things:
                to_put = t.replace(' ', '___')
                mod_text = mod_text.replace(t, to_put)
                mapping[t] = 'SOMETHING'

        return [
            Segment(
                t,
                tag=mapping.get(t, None)
            ) for t in nltk.word_tokenize(mod_text)
        ]

    @cached_property
    def segments(self):
        segments = self.base_segments
        people = self.people

        for person in people:
            segments = replace_sub(segments, [Segment(p) for p in person.split(' ')], [Segment(person, tag='PERSON')])

        return segments

    @cached_property
    def assignments(self):
        return extract_assignments(self)

    @cached_property
    def speech(self):
        return extract_speech(self)
