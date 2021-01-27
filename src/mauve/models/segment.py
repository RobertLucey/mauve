
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
from mauve import (
    GENDER_DETECTOR,
    VADER,
    TAGGER,
    ENCORE,
    WPS,
    SYNONYM,
    Tagger,
    ALL
)

from mauve.utils import (
    get_stem,
    get_lem,
    lower,
    replace_sub,
    get_wordnet_pos
)


class Segment(Tagger):
    '''
    A segment is a word / phrase / group of words that belong together, smallest unit

    This can be like "postman pat", "Department of transport", 'Dr Jones'
    '''

    def __init__(self, text, tag=None):
        '''

        :param text: Text content of the segment
        :kwarg tag: A nltk or spacy tag of the segment
        '''
        if '___' in text:
            text = text.replace('___', ' ')
        ALL[text] += 1
        self._text = SYNONYM.get_word(text.replace(' ', '_'))
        self._tag = tag
        WPS.update()

    def serialize(self):
        return {
            'text': self.text,
            'tag': self.tag,
            'lem_stem': self.lem_stem
        }

    def __eq__(self, other):
        '''
        Are two segments equal. Only considers text as you
        usually don't care about tags
        '''
        return self.text == other.text

    @property
    def is_prp(self):
        return self.tag == 'PRP' or self.tag == 'PRP$'

    @property
    def is_adj(self):
        return self.tag[0] == 'J' and not self.is_entity

    @property
    def is_person(self):
        return self.tag == 'PERSON' or self.is_titled_noun

    @property
    def is_titled_noun(self):
        return any([self.text.lower().startswith(prefix) for prefix in LIKELY_PERSON_PREFIXES])

    @property
    def is_noun(self):
        tag = self.tag
        if tag == '':
            tag = 'Z'

        return any([
            (tag[0] == 'N' and not self.is_entity),
            tag in ['EVENT', 'ORG', 'PERSON', 'PRODUCT', 'NORP', 'FAC', 'GPE', 'LOC', 'WORK_OF_ART', 'LANGUAGE'],
            self.is_titled_noun,
            self.is_person
        ])

    @property
    def is_verb(self):
        return self.tag[0] == 'V' and not self.is_entity

    @property
    def is_adv(self):
        return self.tag[0] == 'R' and not self.is_entity

    @property
    def is_entity(self):
        if self.tag in ['CARDINAL', 'DATE', 'EVENT', 'FAC', 'GPE', 'LANGUAGE', 'LAW', 'LOC', 'MONEY', 'NORP', 'ORDINAL', 'ORG', 'PERCENT', 'PERSON', 'PRODUCT', 'QUANTITY', 'TIME', 'WORK_OF_ART']:
            return True
        return False

    @property
    def text(self):
        return self._text.replace('_', ' ')

    @property
    def lem_stem(self):
        if ' ' in self.text or self.is_entity:
            return self.text

        return get_stem(get_lem(
            self.text,
            get_wordnet_pos(self.tag)
        ))

    @property
    def tag(self):
        if self._tag is not None:
            return self._tag

        if ' ' in self.text or '_' in self.text:
            return 'dunno'

        return self.pos_tag([self.text])[0][1]

    @property
    def is_wordy(self):
        '''
        Is it more wordy than not wordy?

        If any punctuation / numbers other than space and
        underscore will return false
        '''
        return self.text.replace(' ', '').replace('_', '').isalpha()

