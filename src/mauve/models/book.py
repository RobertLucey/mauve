from collections import defaultdict
import pickle
import difflib
import statistics
import json
import os
from collections import Counter
import random

from cached_property import cached_property
import fast_json

import textstat
import nltk
import gender_guesser.detector as gender
from langdetect import detect as langdetect
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from mauve.decorators import kwarg_validator
from mauve.constants import (
    ENG_WORDS,
    PROFANITY_LIST
)

from mauve.models.generic import (
    GenericObject,
    GenericObjects
)
from mauve.models.tag import Tags
from mauve.models.review import Reviews
from mauve.bst import (
    Node,
    create,
    search
)

from mauve.constants import SIMPLE_TOKEN_MAP
from mauve.splunk_push import StreamSubmit


GENDER_DETECTOR = gender.Detector()
VADER = SentimentIntensityAnalyzer()


class Book(GenericObject):

    @kwarg_validator('title', 'author', 'year_published',)
    def __init__(
        self,
        title=None,
        author=None,
        tags=None,
        year_published=None,
        publisher=None,
        isbn=None,
        isbn13=None,
        reviews=None,
        subtitle=None,
        avg_rating=None,
        num_ratings=None
    ):
        self.title = title
        self.author = author  # should support multiple authors
        self.year_published = year_published
        self.tags = tags
        self.publisher = publisher
        self.isbn = isbn
        self.isbn13 = isbn13
        self.subtitle = subtitle
        self.avg_rating = avg_rating
        self.num_ratings = num_ratings

        if tags is None:
            self.tags = Tags()
        else:
            self.tags = tags

        if reviews is None:
            self.reviews = Reviews()
        else:
            self.reviews = reviews

        self.content_path = None

        super(Book, self).__init__()

    def is_genre(self, genre_name):
        return self.tags.contains(genre_name)

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
        words = defaultdict(int)
        count = 0

        original_len = len(self.words)

        tree = create(self.words)
        for curse in PROFANITY_LIST:
            if search(tree, curse) != (0, 0):
                words[curse] += 1
                count += 1

        if count == 0:
            return 0

        div = original_len / 10000.
        return count / div

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
            return len(set(self.dictionary_words)) / len(self.dictionary_words)
        return len(set(self.words)) / len(self.words)

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
            source='books',
            tourcetype='books'
        )

    def serialize(self):
        vader_stats = VADER.polarity_scores([a for a in self.sentences if random.random() < 0.05])  # Need more power but this may be an indication
        return {
            'analysis_version': '7',
            'author_similarity': self.author_similarity,
            'title': self.title,
            'author': self.author,
            'author_gender': self.author_gender,
            'year_published': int(self.year_published),
            'publisher': self.publisher,
            'isbn': self.isbn,
            'isbn13': self.isbn13,
            'subtitle': self.subtitle,
            'avg_rating': float(self.avg_rating),
            'num_ratings': int(self.num_ratings),
            'tags': self.tags.serialize(),
            'reviews': self.reviews.serialize(),
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
            'vader_pos': vader_stats['pos'],
            'vader_neg': vader_stats['neg'],
            'vader_neu': vader_stats['neu'],
            'vader_compound': vader_stats['compound'],
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

    @property
    def epub_path(self):
        # TODO: get the epub of the filename. Not needed so far
        raise NotImplementedError()

    @cached_property
    def lang(self):
        # TODO: update metadata and use as a cache since this can't be very good
        # Also only go far enough until we're certain. Don't need to process entire books
        return langdetect(self.content)

    @cached_property
    def sentences_tokens(self):
        size = len(self.tokens)
        idx_list = [
            idx + 1 for idx, val in enumerate(self.tokens) if val[0] == '.'
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
        author_split = self.author.split(' ')
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
    def content(self):
        '''
        '''
        return open(
            self.content_path,
            'r',
            encoding='latin1'
        ).read()

    @cached_property
    def dictionary_words(self):
        return [
            w for w in self.words if w.lower() in ENG_WORDS or not w.isalpha()
        ]

    @cached_property
    def words(self):
        # TODO: optional preprocess to make it's it is and all that

        if os.path.exists(self.content_path + '.tokenv2.pickle'):
            return [i[0] for i in self.tokens]
        else:
            return nltk.word_tokenize(self.content)

    @cached_property
    def tokens(self):
        data = []
        if os.path.exists(self.content_path + '.tokenv2.pickle'):
            data = pickle.load(open(self.content_path + '.tokenv2.pickle', 'rb'))
        else:
            # XXX can skip here to speed things up once cached

            data = nltk.pos_tag(self.words)

            f_pickle = open(self.content_path + '.tokenv2.pickle', 'wb')
            pickle.dump(data, f_pickle)
            f_pickle.close()

        return data

    @property
    def safe_to_use(self):

        if self.content_path:
            pass
            # make sure the author in the filename is close to the one in the metadata

        if int(self.num_ratings) < 10:
            # if not enough ratings we may have the rating for the wrong
            # book or there may not be enough information to be accurate for this book
            return False

        if int(self.year_published) < 1900:
            return False

        if 'part' in self.title.lower() or 'vol' in self.title.lower() or 'edition' in self.title.lower():
            # Can change stats if a book / series is split
            return False

        if ' and ' in self.author.lower() or '&' in self.author.lower():
            # multiple authors makes things a bit messier for some stats
            # At some point should support multiple authors
            return False

        if not self.author_similarity:
            # Likely not the same author
            return False

        return True

    @property
    def author_similarity(self):

        def matches(first_string, second_string):
            s = difflib.SequenceMatcher(None, first_string, second_string)
            match = [first_string[i:i+n] for i, j, n in s.get_matching_blocks() if n > 0]
            return match

        meta_author = self.author.replace('.', '').lower()
        filename_author = os.path.basename(self.content_path).split('___')[1].replace('.', '').lower()

        try:
            if max([
                len(m) for m in matches(
                    meta_author,
                    filename_author
                )
            ]) > max([
                len(meta_author),
                len(filename_author)
            ]) / 3:
                return True
        except:
            return False

        if meta_author == filename_author:
            return True

        return False

    @property
    def reading_age(self):
        raise NotImplementedError()


class Books(GenericObjects):

    def __init__(self, *args, **kwargs):
        kwargs['child_class'] = Book
        super(Books, self).__init__(*args, **kwargs)
