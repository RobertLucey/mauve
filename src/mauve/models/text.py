from collections import defaultdict
from collections import Counter

import spacy

from spacy.matcher import Matcher

import textacy.ke

from nltk.corpus import wordnet
from nltk.corpus import stopwords
import pickle
import difflib
import statistics
import os
import random

from cached_property import cached_property

import textstat
import gender_guesser.detector as gender
from langdetect import detect as langdetect
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import nltk
from nltk.tag.perceptron import PerceptronTagger
from nltk.tag.mapping import tagset_mapping, map_tag

from mauve.wps import WPS
from mauve.idioms import replace_idioms
from mauve.phrases import replace_phrases
from mauve.utils import get_stem, get_lem, lower, replace_sub
from mauve.decorators import kwarg_validator
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

from mauve.models.generic import (
    GenericObject,
    GenericObjects
)
from mauve.models.books.tag import Tags
from mauve.models.books.review import Reviews
from mauve.bst import (
    Node,
    create,
    search
)
from mauve.models.synonym import Synonym
from mauve.models.assignment import Assignment, extract_assignments

from mauve.splunk_push import StreamSubmit


GENDER_DETECTOR = gender.Detector()
VADER = SentimentIntensityAnalyzer()
TAGGER = PerceptronTagger()
ENCORE = spacy.load('en_core_web_sm')

WPS = WPS(print_rate=10000)

SYNONYM = Synonym()


ALL = defaultdict(int)


class Tagger():

    def pos_tag(self, tokens):
        if tokens == ['']:
            return []

        tagged_tokens = TAGGER.tag(tokens)

        if random.random() < 0.5:
            count = 0
            for tok, tag in tagged_tokens:
                if count % 2 == 0:
                    TAGGER.tagdict[tok] = tag

        return tagged_tokens


class Segment(Tagger):

    def __init__(self, text, tag=None):
        if '___' in text:
            text = text.replace('___', ' ')
        ALL[text] += 1
        self._text = SYNONYM.get_word(text.replace(' ', '_'))
        self._tag = tag
        WPS.update()

    def __eq__(self, other):
        """Overrides the default implementation"""
        return self.text == other.text

    def get_wordnet_pos(self, tag):
        """Map POS tag to first character lemmatize() accepts"""
        tag = tag[0].upper()
        tag_dict = {
            'J': wordnet.ADJ,
            'N': wordnet.NOUN,
            'V': wordnet.VERB,
            'R': wordnet.ADV
        }

        return tag_dict.get(tag, wordnet.NOUN)

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
        return any([
            (self.tag[0] == 'N' and not self.is_entity),
            self.tag in ['EVENT', 'ORG', 'PERSON', 'PRODUCT', 'NORP', 'FAC', 'GPE', 'LOC', 'WORK_OF_ART', 'LANGUAGE'],
            self.is_titled_noun
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
            self.get_wordnet_pos(self.tag)
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
        return self.text.replace(' ', '').replace('_', '').isalpha()


class Sentence():

    def __init__(self, text):
        self.text = text

    @property
    def people(self):
        self.text = replace_phrases(self.text)

        people = []

        prev_was_first = False
        for segment in self.base_segments:
            if any([
                'minister for ' in segment.text.lower(),
                'minister of ' in segment.text.lower()
            ]):
                people.append(segment.text)
            elif segment.tag == 'PERSON' or (
                segment.tag == 'dunno' and (
                    any([segment.text.lower().startswith(prefix) for prefix in LIKELY_PERSON_PREFIXES])
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

    @property
    def assignments(self):
        return extract_assignments(self)

    def previous_current_next(self, iterable):
        """Make an iterator that yields an (previous, current, next) tuple per element.

        Returns None if the value does not make sense (i.e. previous before
        first and next after last).
        """
        iterable = iter(iterable)
        prv = None
        cur = iterable.__next__()
        try:
            while True:
                nxt = iterable.__next__()
                yield (prv, cur, nxt)
                prv = cur
                cur = nxt
        except StopIteration:
            yield (prv, cur, None)

    def preprocess_text(self, text):
        return ' '.join([SYNONYM.get_word(t.replace(' ', '_')) for t in nltk.word_tokenize(text)])

    @cached_property
    def base_segments(self):
        self.text = self.preprocess_text(self.text)

        sentence = ENCORE(self.text.lower())

        mod_text = self.text
        mapping = {}

        for e in sentence.ents:
            to_put = e.text.replace(' ', '___')
            mod_text = mod_text.replace(e.text, to_put)
            mapping[e.text.lower()] = e.label_

        try:
            doc = textacy.make_spacy_doc(mod_text.lower())
        except Exception as ex:
            print(ex)
        else:
            things = [
                k[0] for k in textacy.ke.textrank(
                    doc,
                    normalize='lemma',
                    topn=10
                ) if ' ' in k[0]  # only really care about multi word phrases
            ]

            for t in things:
                to_put = t.replace(' ', '___')
                mod_text = mod_text.replace(t, to_put)
                mapping[t] = 'SOMETHING'

        return [
            Segment(
                t,
                tag=mapping.get(t.lower(), None)
            ) for t in nltk.word_tokenize(mod_text)
        ]

    @cached_property
    def segments(self):
        people = self.people
        segments = self.base_segments

        for person in people:
            segments = replace_sub(segments, [Segment(p) for p in person.split(' ')], [Segment(person, tag='PERSON')])

        return segments



class Text(GenericObject, Tagger):

    @cached_property
    def content(self):
        '''
        '''
        try:
            return open(
                self.content_path,
                'r',
                encoding='latin1'
            ).read()
        except Exception as ex:
            print('BAD FILE: %s' % (self.content_path))
            print(ex)
            return ''

    def set_content_location(self, content_path):
        '''

        :param content_path:
        '''
        self.content_path = content_path

    def get_top_adjectives(self, num_to_get):
        adjs = Counter(
            [a.lower() for a in self.adjectives]
        ).most_common(num_to_get * 2)
        return dict(
            [
                a for a in adjs if all([
                    a[0] in self.dictionary_words,
                    'â' not in str(a),
                    a != 'n'
                ])
            ][0:num_to_get]
        )

    def get_top_nouns(self, num_to_get):
        nouns = Counter(
            [a.lower() for a in self.nouns]
        ).most_common(num_to_get * 2)
        return dict(
            [
                a for a in nouns if all([
                    a[0] in self.dictionary_words,
                    'â' not in str(a),
                    a != 'n'
                ])
            ][0:num_to_get]
        )

    def get_top_verbs(self, num_to_get):
        verbs = Counter(
            [a.lower() for a in self.verbs]
        ).most_common(num_to_get * 2)
        return dict(
            [
                a for a in verbs if all([
                    a[0] in self.dictionary_words,
                    'â' not in str(a),
                    a != 'n'
                ])
            ][0:num_to_get]
        )

    def get_profanity_score(self):
        word_counts = {}
        words = []

        original_len = len(self.words)

        tree = create(self.words)
        for curse in PROFANITY_LIST:
            if search(tree, curse) != (0, 0):
                words.append(curse)

        for w in words:
            word_counts[w] = self.words.count(w)

        if words == []:
            return 0

        div = original_len / 10000.
        return sum(word_counts.values()) / div

    def get_token_type_score(self, token_type):
        assert(token_type in SIMPLE_TOKEN_MAP.values())
        div = len(self.words) / 10000.
        return len([m for m in self.tokens if SIMPLE_TOKEN_MAP[m[1]] == token_type]) / div

    def get_lexical_diversity(self, only_dictionary_words=False):
        '''

        :kwargs only_dictionary_words:
        :return:
        :rtype:
        '''
        if only_dictionary_words:
            return float(len(set(self.dictionary_words))) / len(self.dictionary_words)
        return float(len(set(self.words))) / len(self.words)

    def get_avg_word_len(self, only_dictionary_words=False):
        '''

        :kwargs only_dictionary_words:
        :return:
        :rtype:
        '''
        if only_dictionary_words:
            return statistics.mean([len(i) for i in self.dictionary_words])
        return statistics.mean([len(i) for i in self.words])

    def get_avg_sentence_word_len(self):
        return statistics.mean(
            [len(nltk.word_tokenize(i)) for i in self.sentences]
        )

    def get_avg_sentence_char_len(self):
        return statistics.mean(
            [len(i) for i in self.sentences]
        )

    def push_to_splunk(self):
        StreamSubmit().submit(
            'books',
            self.serialize(),
            source=self.source,
            sourcetype=self.sourcetype
        )

    @cached_property
    def sentiment(self):
        return VADER.polarity_scores([a for a in self.sentences if random.random() < 0.05])  # Need more power but this may be an indication

    def serialize_stats(self):
        return {
            'analysis_version': int(ANALYSIS_VERSION),
            'author': getattr(self, 'author', None),
            'author_gender': self.author_gender,
            'word_count': len(self.words),
            'lexical_diversity': self.get_lexical_diversity(),
            'avg_word_len': self.get_avg_word_len(),
            'profanity_score': self.get_profanity_score(),
            'avg_sentence_word_len': self.get_avg_sentence_word_len(),
            'avg_sentence_char_len': self.get_avg_sentence_char_len(),
            'adverb_score': self.get_token_type_score('adverb'),
            'interjection_score': self.get_token_type_score('interjection'),
            'adjective_score': self.get_token_type_score('adjective'),
            'top_adjectives': self.get_top_adjectives(10),
            'top_nouns': self.get_top_nouns(10),
            'top_verbs': self.get_top_verbs(10),
            'flesch_reading_ease_score': textstat.flesch_reading_ease(self.content),
            'crawford_score': textstat.crawford(self.content),
            'vader_pos': self.sentiment['pos'],
            'vader_neg': self.sentiment['neg'],
            'vader_neu': self.sentiment['neu'],
            'vader_compound': self.sentiment['compound'],
        }

    def __del__(self):
        attrs_to_del = [
            'lang',
            'sentences_tokens',
            'sentences',
            'adverbs',
            'adjectives',
            'nouns',
            'proper_nouns',
            'verbs',
            'author_gender',
            'content',
            'dictionary_words',
            'words',
            'tokens'
        ]

        for attr in attrs_to_del:
            try:
                delattr(self, attr)
            except:
                pass

    @cached_property
    def lang(self):
        # TODO: update metadata and use as a cache since this can't be very good
        # Also only go far enough until we're certain. Don't need to process entire books
        return langdetect(self.content)

    @cached_property
    def sentences_tokens(self):
        size = len(self.tokens)
        idx_list = [
            idx + 1 for idx, val in enumerate(self.tokens) if val[0] in SENTENCE_TERMINATORS
        ]

        return [
            self.tokens[i: j] for i, j in zip(
                [0] + idx_list,
                idx_list + ([size] if idx_list[-1] != size else [])
            )
        ]

    @cached_property
    def sentences(self):
        return nltk.tokenize.sent_tokenize(self.content)

    @cached_property
    def adverbs(self):
        return [m[0] for m in self.tokens if SIMPLE_TOKEN_MAP[m[1]] == 'adverb']

    @cached_property
    def adjectives(self):
        return [m[0] for m in self.tokens if SIMPLE_TOKEN_MAP[m[1]] == 'adjective']

    @cached_property
    def nouns(self):
        return [m[0] for m in self.tokens if SIMPLE_TOKEN_MAP[m[1]] == 'noun']

    @cached_property
    def proper_nouns(self):
        return [m[0] for m in self.tokens if SIMPLE_TOKEN_MAP[m[1]] == 'proper noun']

    @cached_property
    def verbs(self):
        return [m[0] for m in self.tokens if SIMPLE_TOKEN_MAP[m[1]] == 'verb']

    @cached_property
    def author_gender(self):
        try:
            author_split = self.author.split(' ')
        except:
            return

        if '.' in author_split[0]:
            # Try use the author's wikipedia page or something
            return None

        if ' and ' in self.author.lower() or '&' in self.author.lower():
            return None

        gender = GENDER_DETECTOR.get_gender(author_split[0])
        if gender != 'male' and gender != 'female':
            # Try use the author's wikipedia page or something
            return None

        return gender

    @cached_property
    def dictionary_words(self):
        return [
            w.lower() for w in self.words if w.lower() in ENG_WORDS and w.isalpha()
        ]

    @cached_property
    def words(self):
        raise NotImplementedError()

    @cached_property
    def tokens(self):
        raise NotImplementedError()

    @property
    def reading_age(self):
        raise NotImplementedError()

    @property
    def word_count(self):
        return len(self.words)

    def previous_current_next(self, iterable):
        """Make an iterator that yields an (previous, current, next) tuple per element.

        Returns None if the value does not make sense (i.e. previous before
        first and next after last).
        """
        iterable = iter(iterable)
        prv = None
        cur = iterable.__next__()
        try:
            while True:
                nxt = iterable.__next__()
                yield (prv, cur, nxt)
                prv = cur
                cur = nxt
        except StopIteration:
            yield (prv, cur, None)

    def get_wordnet_pos(self, tag):
        """Map POS tag to first character lemmatize() accepts"""
        tag = tag[0].upper()
        tag_dict = {'J': wordnet.ADJ,
                    'N': wordnet.NOUN,
                    'V': wordnet.VERB,
                    'R': wordnet.ADV}

        return tag_dict.get(tag, wordnet.NOUN)

    @cached_property
    def phrases_content(self):
        try:
            return replace_phrases(self.content)
        except:
            print('Skipping content')

    def preprocess_text(self, text):
        return ' '.join([SYNONYM.get_word(t.replace(' ', '_')) for t in nltk.word_tokenize(text)])

    @property
    def assignments(self):
        '''
        x is (quite, very) y, factor in much like how 'Ham is very tasy' and 'Ham is not tasty' are exact opposites
        '''

        mapping = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        phrases_content = self.preprocess_text(self.phrases_content)

        if phrases_content is None:
            return {}

        for s in nltk.tokenize.sent_tokenize(phrases_content):

            sentence = Sentence(s)
            assignments = sentence.assignments

            for x in assignments:
                print(x.serialize())
                #print(sentence.text)
                #print('%s=%s    %s' % (x.left, x.right, x.extra))
        return mapping
