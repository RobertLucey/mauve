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

    def should_include(self, book):
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

        :kwarg min_per_group: The minimum required items for the
            entire tag / group to be processed
        """
        self.items = []
        self.docs = []
        self.num_items = 0
        self.counter = defaultdict(int)
        self.min_per_group = min_per_group

    def load(self, item):
        if self.should_include(item):
            self.items.append(item)
            self.num_items += 1

    def should_include(self, item):
        raise NotImplementedError()

    def get_group_name(self, item):
        raise NotImplementedError()

    def __iter__(self):
        for item in self.items:
            group = self.get_group_name(item)
            yield TaggedDocument(
                self.content_cleaner(item).split(),
                [str(group + '_%s') % (self.counter[group])]
            )
            self.counter[group] += 1

    def to_array(self):
        self.docs = [i for i in self]
        return self.docs

    def perm(self):
        shuffle(self.docs)
        return self.docs

    def content_cleaner(self, item):
        return item.content

    def clean_data(self):

        def cull(skip_lang, multi=0):
            groups_count = defaultdict(int)
            for item in self.items:
                if self.get_group_name(item) is not None:
                    groups_count[self.get_group_name(item)] += 1

            if skip_lang:
                self.items = [
                    item for item in self.items if groups_count[self.get_group_name(item)] >= self.min_per_group
                ]
            else:
                self.items = [
                    item for item in self.items if item.lang == 'en'
                ]

            groups_count = defaultdict(int)
            for item in self.items:
                if self.get_group_name(item) is not None:
                    groups_count[self.get_group_name(item)] += 1

            group_items_map = defaultdict(list)
            for item in self.items:
                group_items_map[self.get_group_name(item)].append(item)
            self.items = flatten([v[0:int(self.min_per_group * multi)] for k, v in group_items_map.items()])

        cull(skip_lang=True, multi=2)
        cull(skip_lang=False, multi=2)
        cull(skip_lang=True, multi=1)

        group_counts = defaultdict(int)
        for item in self.items:
            if self.get_group_name(item) is not None:
                group_counts[self.get_group_name(item)] += 1

        cleaned_items = []
        for name, count in group_counts.items():
            group_count = 0
            for item in self.items:
                if self.get_group_name(item) == name:
                    if group_count < self.min_per_group:
                        cleaned_items.append(item)
                        group_count += 1

        self.items = cleaned_items

        group_counts = defaultdict(int)
        for item in self.items:
            if self.get_group_name(item) is not None:
                group_counts[self.get_group_name(item)] += 1

        for name, count in group_counts.items():
            logger.debug('%s: %s', name, count)


class AuthorTaggedDocs(Safety, BaseTaggedDocs):

    def __init__(self, *args, **kwargs):
        self.authors = kwargs.pop('authors', [])
        super(AuthorTaggedDocs, self).__init__(*args, **kwargs)

    def content_cleaner(self, book):
        return book.content.replace(book.author.name, '')

    def get_group_name(self, book):
        return book.author.name


class GenderTaggedDocs(Safety, BaseTaggedDocs):

    def get_group_name(self, book):
        return book.author.gender


class NationalityTaggedDocs(Safety, BaseTaggedDocs):

    def get_group_name(self, book):
        nationality = book.author.nationality

        if nationality is None:
            return None

        if nationality in ['England', 'Scotland', 'Wales']:
            return 'British'

        if ',' in nationality or '–' in nationality:
            return None

        return nationality


class AgeTaggedDocs(Safety, BaseTaggedDocs):

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
