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

    @mock.patch('mauve.models.books.book.Book.content', 'one one asdasd')
    def test_get_lexical_diversity_dictionary(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertEquals(1/2., book.get_lexical_diversity(only_dictionary_words=True))

    @mock.patch('mauve.models.books.book.Book.content', 'go go run')
    def test_get_top_verbs(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertEquals(book.get_top_verbs(10), {'go': 2, 'run': 1})

    @mock.patch('mauve.models.books.book.Book.content', 'big ball happy happy')
    def test_get_top_adjectives(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertEquals(book.get_top_adjectives(10), {'happy': 2, 'big': 1})

    @mock.patch('mauve.models.books.book.Book.content', 'pencil and pencil house')
    def test_get_top_nouns(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertEquals(book.get_top_nouns(10), {'pencil': 2, 'house': 1})

    @mock.patch('mauve.models.books.book.Book.content', 'I\'m a little teapot. Really, I am! Right?')
    def test_sentences_tokens(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertEquals(
            book.sentences_tokens,
            [
                [('I', 'PRP'), ("'m", 'VBP'), ('a', 'DT'), ('little', 'JJ'), ('teapot', 'NN'), ('.', '.')],
                [('Really', 'RB'), (',', ','), ('I', 'PRP'), ('am', 'VBP'), ('!', '.')],
                [('Right', 'NNP'), ('?', '.')]
            ]
        )

    @mock.patch('mauve.models.books.book.Book.content', 'Do it quietly')
    def test_adverbs(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertEquals(book.adverbs, ['quietly'])

    @mock.patch('mauve.models.books.book.Book.content', 'It is blue')
    def test_adjectives(self):
        book = Book(title='t', author='a', year_published=1)
        book.set_content_location('/tmp/mauve_tok')
        self.assertEquals(book.adjectives, ['blue'])


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

    def test_author_gender(self):
        book = Book(title='t', author='Arthur', year_published=2020, num_ratings=100)
        self.assertEqual(book.author_gender, 'male')

        book = Book(title='t', author='Alice McArthur', year_published=2020, num_ratings=100)
        self.assertEqual(book.author_gender, 'female')

        book = Book(title='t', author=None, year_published=2020, num_ratings=100)
        self.assertEqual(book.author_gender, None)
