from unittest import TestCase
import mock

import glob
import os

from mauve.models.books.book import Book
from mauve.models.books.tag import Tags, Tag


class TestBook(TestCase):

    def tearDown(self):
        for f in glob.glob('/tmp/mauve_tok*'):
            os.remove(f)


    def test_is_genre(self):
        tags = Tags()
        tags.append(Tag(name='something'))
        tags.append(Tag(name='something else'))
        book = Book(title='t', author='a', year_published=1, tags=tags)
        self.assertFalse(book.is_genre('som'))
        self.assertTrue(book.is_genre('something'))


    @mock.patch('mauve.models.books.book.Book.content', 'fuck')
    def test_get_profanity_score(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertAlmostEqual(10000, book.get_profanity_score())

    @mock.patch('mauve.models.books.book.Book.content', 'nice')
    def test_get_profanity_score_2(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertAlmostEqual(0, book.get_profanity_score())

    @mock.patch('mauve.models.books.book.Book.content', 'fuck fuck nice')
    def test_get_profanity_score_3(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertAlmostEqual((2/3.)*10000, book.get_profanity_score())

    @mock.patch('mauve.models.books.book.Book.content', 'run small big')
    def test_get_token_type_score(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertAlmostEqual((2/3.)*10000, book.get_token_type_score('adjective'))
        self.assertAlmostEqual((1/3.)*10000, book.get_token_type_score('verb'))

    @mock.patch('mauve.models.books.book.Book.content', 'one two three')
    def test_get_lexical_diversity(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertEquals(1., book.get_lexical_diversity())

    @mock.patch('mauve.models.books.book.Book.content', 'one one one')
    def test_get_lexical_diversity_2(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertEquals(1/3., book.get_lexical_diversity())

    def test_author_similarity(self):
        book = Book(title='t', author='Author', year_published=1)
        book.set_content_location('/tmp/mauve/isbn___Author___title.txt')
        self.assertTrue(book.author_similarity)

        book = Book(title='t', author='Author', year_published=1)
        book.set_content_location('/tmp/mauve/isbn___Author Something___title.txt')
        self.assertTrue(book.author_similarity)

        book = Book(title='t', author='Author', year_published=1)
        book.set_content_location('/tmp/mauve/isbn___Something Author___title.txt')
        self.assertTrue(book.author_similarity)

        book = Book(title='t', author='Arthur', year_published=1)
        book.set_content_location('/tmp/mauve/isbn___Something Author___title.txt')
        self.assertFalse(book.author_similarity)

    def test_safe_to_use(self):
        book = Book(title='t', author='Author', year_published=2020, num_ratings=100)
        book.set_content_location('/tmp/mauve/isbn___Something Author___title.txt')
        self.assertTrue(book.safe_to_use)

        book = Book(title='t', author='Author', year_published=2020, num_ratings=0)
        book.set_content_location('/tmp/mauve/isbn___Something Author___title.txt')
        self.assertFalse(book.safe_to_use)

        book = Book(title='t', author='Author', year_published=1700, num_ratings=100)
        book.set_content_location('/tmp/mauve/isbn___Something Author___title.txt')
        self.assertFalse(book.safe_to_use)

        book = Book(title='t', author='Arthur', year_published=2020, num_ratings=100)
        book.set_content_location('/tmp/mauve/isbn___Something Author___title.txt')
        self.assertFalse(book.safe_to_use)
