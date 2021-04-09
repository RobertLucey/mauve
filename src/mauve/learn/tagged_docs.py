import logging
from random import shuffle
from collections import defaultdict

from gensim import utils
from gensim.models.doc2vec import TaggedDocument

from mauve.constants.names import NAMES
from mauve.utils import round_down, flatten
from mauve.constants import (
    BORING_WORDS,
    ENG_WORDS,
    EXTENDED_PUNCTUATION
)

logger = logging.getLogger('mauve')


class Safety:
    """
    Just a general filter for all books
    """

    def should_include_book(self, book):
        if self.get_group_name(book) is None:
            return False
        if book.num_ratings < 1000:
            return False
        if not book.author_similarity:
            return False
        if not book.is_genre('fiction'):
            return False
        return True


class BaseTaggedDocs(object):

    def __init__(self, min_per_group=10):
        """

        :kwarg min_per_group: The minimum required books for the
            entire tag / group to be processed
        """
        self.books = []
        self.docs = []
        self.num_books = 0
        self.counter = defaultdict(int)
        self.min_per_group = min_per_group

    def load(self, book):
        if self.should_include_book(book):
            self.books.append(book)
            self.num_books += 1

    def should_include_book(self, book):
        raise NotImplementedError()

    def get_group_name(self, book):
        raise NotImplementedError()

    def __iter__(self):
        for book in self.books:
            group = self.get_group_name(book)
            yield TaggedDocument(
                self.content_cleaner(book).split(),
                [str(group + '_%s') % (self.counter[group])]
            )
            self.counter[group] += 1

    def to_array(self):
        self.docs = [i for i in self]
        return self.docs

    def perm(self):
        shuffle(self.docs)
        return self.docs

    def content_cleaner(self, book):
        return book.content

    def clean_data(self):

        def cull(skip_lang, multi=0):
            groups_count = defaultdict(int)
            for book in self.books:
                if self.get_group_name(book) is not None:
                    groups_count[self.get_group_name(book)] += 1

            if skip_lang:
                self.books = [
                    book for book in self.books if groups_count[self.get_group_name(book)] >= self.min_per_group
                ]
            else:
                self.books = [
                    book for book in self.books if book.lang == 'en'
                ]

            groups_count = defaultdict(int)
            for book in self.books:
                if self.get_group_name(book) is not None:
                    groups_count[self.get_group_name(book)] += 1

            group_books_map = defaultdict(list)
            for book in self.books:
                group_books_map[self.get_group_name(book)].append(book)
            self.books = flatten([v[0:int(self.min_per_group * multi)] for k, v in group_books_map.items()])

        cull(skip_lang=True, multi=2)
        cull(skip_lang=False, multi=2)
        cull(skip_lang=True, multi=1)

        group_counts = defaultdict(int)
        for book in self.books:
            if self.get_group_name(book) is not None:
                group_counts[self.get_group_name(book)] += 1

        cleaned_books = []
        for name, count in group_counts.items():
            group_count = 0
            for book in self.books:
                if self.get_group_name(book) == name:
                    if group_count < self.min_per_group:
                        cleaned_books.append(book)
                        group_count += 1

        self.books = cleaned_books

        group_counts = defaultdict(int)
        for book in self.books:
            if self.get_group_name(book) is not None:
                group_counts[self.get_group_name(book)] += 1

        for name, count in group_counts.items():
            logger.debug('%s: %s', name, count)


class AuthorTaggedDocs(BaseTaggedDocs, Safety):

    def __init__(self, *args, **kwargs):
        self.authors = kwargs.pop('authors', [])
        super(AuthorTaggedDocs, self).__init__(*args, **kwargs)

    def content_cleaner(self, book):
        return book.content.replace(book.author.name, '')

    def get_group_name(self, book):
        return book.author.name


class GenderTaggedDocs(BaseTaggedDocs, Safety):

    def get_group_name(self, book):
        return book.author.gender


class NationalityTaggedDocs(BaseTaggedDocs, Safety):

    def get_group_name(self, book):
        nationality = book.author.nationality

        if nationality is None:
            return None

        if nationality in ['England', 'Scotland', 'Wales']:
            return 'British'

        if ',' in nationality or '–' in nationality:
            return None

        return nationality


class AgeTaggedDocs(BaseTaggedDocs, Safety):

    # Can create a by the decade one handy from this
    # FIXME: This one is a bit crap

    def __iter__(self):
        for book in self.books:
            group = self.get_group_name(book)

            yield TaggedDocument(
                [w for w in utils.to_unicode(self.content_cleaner(book)).split() if (w in NAMES) or (w not in BORING_WORDS and w in ENG_WORDS and w not in EXTENDED_PUNCTUATION)],
                [str(group + '_%s') % (self.counter[group])]
            )
            self.counter[group] += 1

    def get_group_name(self, book):
        try:
            if round_down(book.year_published - book.author.birth_year, 10) >= 70:
                return
            return str(round_down(book.year_published - book.author.birth_year, 10))
        except:
            return
