import pickle
import difflib
import os
import random
import statistics
from collections import Counter

from cached_property import cached_property

import numpy
import textstat
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from mauve.decorators import kwarg_validator
from mauve.models.generic import GenericObjects
from mauve.models.person import (
    Author,
    Person
)
from mauve.models.books.tag import Tags
from mauve.models.books.review import Reviews
from mauve.models.text import TextBody
from mauve.constants import (
    LOUD_WORDS,
    SIMPLE_TOKEN_MAP,
    TOKEN_VERSION,
    ANALYSIS_VERSION
)
from mauve.utils import (
    str_count_multi,
    get_file_content,
    get_loose_filepath
)
from mauve import GENDER_DETECTOR


VADER = SentimentIntensityAnalyzer()


class Book(TextBody):

    @kwarg_validator('title', 'author',)
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
        num_ratings=None,
        content_path=None
    ):
        self.title = title
        self.author = Author(name=getattr(author, 'name', author))  # should support multiple authors
        self.year_published = int(year_published) if year_published is not None else None
        self.tags = tags
        self.publisher = publisher
        self.isbn = isbn
        self.isbn13 = isbn13
        self.subtitle = subtitle
        self.avg_rating = float(avg_rating) if avg_rating is not None else None
        self.num_ratings = int(num_ratings) if num_ratings is not None else None
        self.tags = tags if tags is not None else Tags()
        self.reviews = reviews if reviews is not None else Reviews()

        super(Book, self).__init__(content_path=content_path)

    def is_genre(self, genre_name):
        return self.tags.contains(genre_name)

    def serialize(self):
        vader_stats = VADER.polarity_scores([a for a in self.sentences])  # Need more power but this may be an indication
        return {
            'analysis_version': int(ANALYSIS_VERSION),
            'author_similarity': self.author_similarity,
            'title': self.title,
            'author': self.author.name,
            'author_gender': self.author.gender,
            'author_nationality': self.author.nationality,
            'author_birth_year': self.author.birth_year,
            'year_published': int(self.year_published),
            'publisher': self.publisher,
            'isbn': self.isbn,
            'isbn13': self.isbn13,
            'subtitle': self.subtitle,
            'avg_rating': float(self.avg_rating) if self.avg_rating else None,
            'num_ratings': int(self.num_ratings) if self.num_ratings else None,
            'tags': self.tags.serialize(),
            'reviews': self.reviews.serialize(),
            'word_count': self.word_count,
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
            'reading_difficulty': self.reading_difficulty,
            'reading_time': self.reading_time,
            'vader_pos': vader_stats['pos'],
            'vader_neg': vader_stats['neg'],
            'vader_neu': vader_stats['neu'],
            'vader_compound': vader_stats['compound'],
        }

    def __del__(self):
        attrs_to_del = [
            '_all_tokens_count',
            'adverbs',
            'adjectives',
            'nouns',
            'proper_nouns',
            'verbs',
            'adverbs',
            'adjectives',
            'nouns',
            'proper_nouns',
            'verbs',
            'author_gender'
        ]

        for attr in attrs_to_del:
            try:
                delattr(self, attr)
            except:
                pass

    @property
    def reading_time(self):
        # 4.166 is words per second
        return self.word_count / 4.166

    @property
    def reading_difficulty(self):
        """
        Estimate how difficult the book is to read.
        This doesn't consider the length of a book since I don't think
        that's the right kind of difficulty to focus on.
        """
        syllable_scores = []
        difficulty_scores = []
        for sentence in self.sentences:
            total_words = textstat.textstat.lexicon_count(sentence)
            if total_words > 0:
                total_syllables = textstat.textstat.syllable_count(sentence)
                syllables_per_words = (total_syllables / total_words)

                words = textstat.remove_punctuation(sentence)

                # Removes with upper start as possible proper name
                # Bit sloppy but closer to truth than not removing them
                difficult_words = [
                    word for word in words if textstat.is_difficult_word(
                        word,
                        syllable_threshold=0
                    ) and not word[0].isupper()
                ]

                difficulty_scores.append(len(difficult_words) / len(words))
                syllable_scores.append(syllables_per_words)
        if len(syllable_scores) < 2:
            return 0

        return numpy.mean(syllable_scores) * (
            1 + numpy.mean(difficulty_scores)
        )

    @property
    def safe_to_use(self):

        if self.num_ratings is None or self.year_published is None:
            return False

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

        if ' and ' in self.author.name.lower() or '&' in self.author.name.lower():
            # multiple authors makes things a bit messier for some stats
            # At some point should support multiple authors
            return False

        if not self.author_similarity:
            # Likely not the same author
            return False

        return True

    @property
    def author_similarity(self):
        filename_author = os.path.basename(self.content_path).split('___')[1].replace('.', '').lower()
        return self.author.is_similar_to(Person(name=filename_author))

    def get_avg_word_len(self, only_dictionary_words=False):
        '''

        :kwargs only_dictionary_words:
        :return:
        :rtype:
        '''
        if only_dictionary_words:
            return numpy.mean([len(i) for i in self.dictionary_words])
        return numpy.mean([len(i) for i in self.words])

    def get_avg_sentence_word_len(self):
        return numpy.mean(
            [len(nltk.word_tokenize(i)) for i in self.sentences]
        )

    def get_avg_sentence_char_len(self):
        return numpy.mean(
            [len(i) for i in self.sentences]
        )

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

    @cached_property
    def _all_tokens_count(self):
        return Counter([SIMPLE_TOKEN_MAP.get(m[1], 'NA') for m in self.all_tokens])

    def get_token_type_score(self, token_type):
        assert (token_type in SIMPLE_TOKEN_MAP.values())
        return self._all_tokens_count[token_type] / (self.word_count / 10000)

    def get_loudness_score(self):
        return str_count_multi(self.words, LOUD_WORDS) / (self.word_count / 10000.)

    @cached_property
    def adverbs(self):
        return [m[0] for m in self.word_tokens if SIMPLE_TOKEN_MAP[m[1]] == 'adverb']

    @cached_property
    def adjectives(self):
        return [m[0] for m in self.word_tokens if SIMPLE_TOKEN_MAP[m[1]] == 'adjective']

    @cached_property
    def nouns(self):
        return [m[0] for m in self.word_tokens if SIMPLE_TOKEN_MAP[m[1]] == 'noun']

    @cached_property
    def proper_nouns(self):
        return [m[0] for m in self.word_tokens if SIMPLE_TOKEN_MAP[m[1]] == 'proper noun']

    @cached_property
    def verbs(self):
        return [m[0] for m in self.word_tokens if SIMPLE_TOKEN_MAP[m[1]] == 'verb']


class Books(GenericObjects):

    def __init__(self, *args, **kwargs):
        kwargs['child_class'] = Book
        super(Books, self).__init__(*args, **kwargs)
