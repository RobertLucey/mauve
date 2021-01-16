import pickle
import difflib
import os
import random

from cached_property import cached_property

import textstat
import nltk
import gender_guesser.detector as gender
from langdetect import detect as langdetect
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from mauve.decorators import kwarg_validator
from mauve.models.generic import GenericObjects
from mauve.models.books.tag import Tags
from mauve.models.books.review import Reviews
from mauve.splunk_push import StreamSubmit
from mauve.models.text import Text
from mauve.constants import TOKEN_VERSION
from mauve.utils import (
    get_file_content,
    get_loose_filepath
)


VADER = SentimentIntensityAnalyzer()


class Book(Text):

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

    @cached_property
    def words(self):
        # TODO: optional preprocess to make it's it is and all that

        if self.content_path is None:
            return []

        if os.path.exists(self.pickle_path):
            return [i[0] for i in self.tokens]
        else:
            return nltk.word_tokenize(self.content)

    @cached_property
    def tokens(self):

        # TODO: first off try to get from non compressed then try get from compressed

        data = []
        if get_loose_filepath(self.pickle_path):
            data = get_file_content(self.pickle_path)
        else:
            # XXX can skip here to speed things up once cached

            data = nltk.pos_tag(self.words)

            try:
                f_pickle = open(self.pickle_path, 'wb')
                pickle.dump(data, f_pickle)
                f_pickle.close()
            except Exception as ex:
                print('Could not open file %s: %s' % (self.pickle_path, ex))

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
    def pickle_path(self):
        return self.content_path + '.tokenv{}.pickle'.format(TOKEN_VERSION)


class Books(GenericObjects):

    def __init__(self, *args, **kwargs):
        kwargs['child_class'] = Book
        super(Books, self).__init__(*args, **kwargs)
