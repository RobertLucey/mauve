import logging
from random import shuffle
from collections import defaultdict

from gensim import utils
from gensim.models.doc2vec import TaggedDocument


logger = logging.getLogger('mauve')


class BaseTaggedDocs(object):

    def __init__(self):
        self.books = []
        self.docs = []
        self.num_books = 0
        self.counter = defaultdict(int)

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
                utils.to_unicode(self.content_cleaner(book.content)).split(),
                [str(group + '_%s') % (self.counter[group])]
            )
            self.counter[group] += 1

    def to_array(self):
        self.docs = [i for i in self]
        return self.docs

    def perm(self):
        shuffle(self.docs)
        return self.docs

    def content_cleaner(self, content):
        return content

    def clean_data(self):
        pass


class AuthorTaggedDocs(BaseTaggedDocs):

    def __init__(self, *args, **kwargs):
        self.authors = kwargs.pop('authors', [])
        super(AuthorTaggedDocs, self).__init__(*args, **kwargs)

    def content_cleaner(self, content):
        for author in self.authors:
            # TODO: make this a bit better
            content = content.replace(author, '')
        return content

    def should_include_book(self, book):
        if book.author.name not in self.authors and self.authors != []:
            return False
        if self.get_group_name(book) is None:
            return False
        return True

    def get_group_name(self, book):
        return book.author.name

    def clean_data(self):

        def cull():
            author_count = defaultdict(int)
            for book in self.books:
                if book.author.name is not None:
                    author_count[book.author.name] += 1

            self.books = [
                book for book in self.books if all([
                    author_count[book.author.name] > 2,
                    book.lang == 'en'
                ])
            ]

        cull()
        cull()

        logger.debug('Author counts')
        author_count = defaultdict(int)
        for book in self.books:
            if book.author.name is not None:
                author_count[book.author.name] += 1

        for name, count in author_count.items():
            logger.debug('%s: %s', name, count)


class GenderTaggedDocs(BaseTaggedDocs):

    def should_include_book(self, book):
        if self.get_group_name(book) is None:
            return False
        if not book.is_genre('fiction'):
            return False
        if book.lang != 'en':
            return False
        return True

    def get_group_name(self, book):
        return book.author.gender
