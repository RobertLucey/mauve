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
from mauve.utils import get_stem, get_lem, lower
from mauve.decorators import kwarg_validator
from mauve.constants import (
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

from mauve.splunk_push import StreamSubmit


GENDER_DETECTOR = gender.Detector()
VADER = SentimentIntensityAnalyzer()
TAGGER = PerceptronTagger()
ENCORE = spacy.load('en_core_web_sm')

WPS = WPS(print_rate=10000)




class Tagger():

    def pos_tag(self, tokens, tagset=None):
        if tokens == ['']:
            return []

        tagged_tokens = TAGGER.tag(tokens, use_tagdict=True)
        if tagset:  # Maps to the specified tagset.
            tagged_tokens = [
                (token, map_tag("en-ptb", tagset, tag)) for (token, tag) in tagged_tokens
            ]

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
        self.text = text
        self._tag = tag
        WPS.update()

    def get_wordnet_pos(self, tag):
        """Map POS tag to first character lemmatize() accepts"""
        tag = tag[0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}

        return tag_dict.get(tag, wordnet.NOUN)

    @property
    def is_entity(self):
        if self.tag in ['CARDINAL', 'DATE', 'EVENT', 'FAC', 'GPE', 'LANGUAGE', 'LAW', 'LOC', 'MONEY', 'NORP', 'ORDINAL', 'ORG', 'PERCENT', 'PERSON', 'PRODUCT', 'QUANTITY', 'TIME', 'WORK_OF_ART']:
            return True
        return False

    @property
    def lem(self):
        if ' ' in self.text or self.is_entity:
            return self.text

        return get_lem(
            self.text,
            self.get_wordnet_pos(self.tag)
        )

    @property
    def tag(self):
        if self._tag is not None:
            return self._tag

        if ' ' in self.text:
            return 'dunno'
        else:
            return self.pos_tag([self.text])[0][1]

    @property
    def is_wordy(self):
        return self.text.replace(' ', '').isalpha()


class Sentence():

    def __init__(self, text):
        self.text = text

    @property
    def segments(self):
        sentence = ENCORE(self.text.lower())

        mod_text = self.text
        mapping = {}

        texty = True
        if texty:
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

        else:

            for e in sentence.ents:
                to_put = e.text.replace(' ', '___')
                mod_text.replace(e.text, to_put)
                mapping[e.text] = e.label_

        return [Segment(t, tag=mapping.get(t.lower(), None)) for t in nltk.word_tokenize(mod_text)]




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
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}

        return tag_dict.get(tag, wordnet.NOUN)

    @cached_property
    def phrases_content(self):
        try:
            return replace_phrases(self.content)
        except:
            print('Skipping content')

    @property
    def assignments(self):
        '''
        x is (quite, very) y, factor in much like how 'Ham is very tasy' and 'Ham is not tasty' are exact opposites
        '''

        original_joining_words = ['does', 'is', 'are', 'am', 'was', 'were']
        joining_words = original_joining_words + ['doe', 'be', 'be', 'be', 'wa', 'be']

        mapping = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        stop_words = set(stopwords.words("english")) - set(joining_words) - set(['we', 'i', 'you', 'not', 'no'])

        phrases_content = self.phrases_content
        if phrases_content is None:
            return {}

        for s in nltk.tokenize.sent_tokenize(phrases_content):

            sentence = Sentence(s)

            good = False
            for w in joining_words:
                if ' ' + w + ' ' in sentence.text:
                    good = True
                    break

            if not good:
                continue

            smaller_sentence = []
            for w in sentence.segments:
                if w.text.lower() not in stop_words:
                    smaller_sentence.append(w)

            # do toks here to not include stemmed

            interesting = False
            interesting_map = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
            for p, c, n in self.previous_current_next(smaller_sentence):

                if not p or not c or not n:
                    continue

                if not p.is_wordy or not n.is_wordy:
                    continue

                ###
                #if SIMPLE_TOKEN_MAP[p[1]] != 'noun':
                #    continue

                #if p[1] not in LIKELY_WORD_TOKENS:
                #    continue

                #if n[1] not in LIKELY_WORD_TOKENS:
                #    continue

                if n.text.lower() in ['to', 'a', 'also', 'in', 'its', 'the', 'at', 'now', 'not', 'very', 'of', 'sure', 'which', 'an', 'more', 'that', 'too', 'almost']:
                    continue

                if c.text.lower() in original_joining_words:

                    #import pdb; pdb.set_trace()

                    #if p.text.lower() in ['there', 'that']:  # too vague
                    #    continue

                    p = lower(p.lem)#text)
                    n = lower(n.lem)#text)

                    mapping[p][n][n] += 1
                    interesting_map[p][n][n] += 1
                    interesting += 1

            #if interesting:
            #    print('\n----------')
            #    print(s)
            #    print([s.text for s in smaller_sentence])
            #    #print(' '.join(words))
            #    #for k, v in interesting_map.items():
            #    #    for ivk, ivv in v.items():
            #    #        print(k + ': ' + ivk + ' ' + str(ivv))

        return mapping
