import copy

from unittest import TestCase

from gensim import utils
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec

from mauve.models.books.book import Book
from mauve.learn.tagged_docs import BaseTaggedDocs


class AlwaysIncludeBaseTaggedDocs(BaseTaggedDocs):

    def should_include(self, book):
        return True

    def get_group_name(self, book):
        return book.title


class TestBaseTaggedDocs(TestCase):

    def test_load(self):
        base = AlwaysIncludeBaseTaggedDocs()
        self.assertEqual(base.items, [])
        self.assertEqual(base.num_items, 0)
        book = Book(title='t', author='a', year_published=0)
        base.load(book)
        self.assertEqual(base.items, [book])
        self.assertEqual(base.num_items, 1)

    def test_iter(self):
        base = AlwaysIncludeBaseTaggedDocs()
        books = [
            Book(title='1', author='a', year_published=0),
            Book(title='2', author='a', year_published=0)
        ]
        base.load(books[0])
        base.load(books[1])

        for idx, b in enumerate(base):
            if idx == 0:
                self.assertEqual(b.tags, ['1_0'])
            else:
                self.assertEqual(b.tags, ['2_0'])

    def test_to_array(self):
        base = AlwaysIncludeBaseTaggedDocs()
        books = [
            Book(title='1', author='a', year_published=0),
            Book(title='2', author='a', year_published=0)
        ]
        base.load(books[0])
        base.load(books[1])

        copied_base = copy.deepcopy(base)

        self.assertEqual(base.to_array(), list([i for i in copied_base]))
