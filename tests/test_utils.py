from unittest import TestCase
import mock

from pathlib import Path
import json
import bz2
import shutil
import glob
import os

from mauve.models.book import Book
from mauve.constants import (
    TEXT_PATH,
    EPUB_PATH,
    CLEAN_EPUB_PATH,
    OIREACHTAS_DIR,
    TOKEN_VERSION,
    GOODREADS_METADATA_PATH
)
from mauve.utils import (
    loose_exists,
    get_loose_filepath,
    compress_file,
    get_file_content,
    get_metadata,
    iter_books
)

from .utils import create_epub


class TestUtils(TestCase):

    def write(self, fp, content):
        f = open(fp, 'w')
        f.write(content)
        f.close()

    def setUp(self):
        try:
            shutil.rmtree('/tmp/mauve')
        except:
            pass

        Path(EPUB_PATH).mkdir(parents=True, exist_ok=True)
        Path(CLEAN_EPUB_PATH).mkdir(parents=True, exist_ok=True)
        Path(TEXT_PATH).mkdir(parents=True, exist_ok=True)
        Path(OIREACHTAS_DIR).mkdir(parents=True, exist_ok=True)
        Path(GOODREADS_METADATA_PATH).mkdir(parents=True, exist_ok=True)

        self.dirty_epub_1 = os.path.join(EPUB_PATH, 'Title Title.epub')
        self.dirty_epub_2 = os.path.join(EPUB_PATH, 'Another Great Title.epub')
        self.clean_epub_1 = os.path.join(CLEAN_EPUB_PATH, '9783161484102___Author A. Author___Another Great Title.epub')

        self.text_path_1 = os.path.join(TEXT_PATH, 'isbn___author___title1.txt')
        self.text_path_2 = os.path.join(TEXT_PATH, 'isbn___author___title2.txt')
        self.text_path_3 = os.path.join(TEXT_PATH, 'isbn___author___title3.txt')

        self.write(self.text_path_1, 'blah blah blah')
        self.write(self.text_path_2, 'blah blah blah')
        self.write(self.text_path_3, 'blah blah blah')

        # a dirty epub
        create_epub(
            isbn='978-3-16-148410-0',
            title='Title title',
            author='Author A. Author',
            content='blah blah blah',
            fp=self.dirty_epub_1
        )

        # a dirty epub
        create_epub(
            isbn='978-3-16-148410-1',
            title='Another Great Title',
            author='Author A. Author',
            content='blah blah blah',
            fp=self.dirty_epub_2
        )

        # a cleaned dirty epub (Title Title)
        create_epub(
            isbn='978-3-16-148410-2',
            title='Another Great Title',
            author='Author A. Author',
            content='blah blah blah',
            fp=self.clean_epub_1
        )

        self.write(
            os.path.join(GOODREADS_METADATA_PATH, 'title_id_map.json'),
            json.dumps(
                {
                    'text_path_1': self.text_path_1,
                    'text_path_2': self.text_path_2,
                    'text_path_3': self.text_path_3
                }
            )
        )

        self.write(
            os.path.join(GOODREADS_METADATA_PATH, 'text_path_1.json'),
            json.dumps(
                {
                    'book_id': 'text_path_1',
                    'book_title': 'Title 1',
                    'genres': ['fiction', 'classics'],
                    'isbn': '',
                    'isbn13': '',
                    'year_first_published': '0',
                    'author': '',
                    'average_rating': '0',
                    'num_ratings': '0',
                }
            )
        )

        self.write(
            os.path.join(GOODREADS_METADATA_PATH, 'text_path_2.json'),
            json.dumps(
                {
                    'book_id': 'text_path_2',
                    'book_title': 'Title 2',
                    'genres': ['fiction', 'classics'],
                    'isbn': '',
                    'isbn13': '',
                    'year_first_published': '0',
                    'author': '',
                    'average_rating': '0',
                    'num_ratings': '0',
                }
            )
        )

        self.write(
            os.path.join(GOODREADS_METADATA_PATH, 'text_path_3.json'),
            json.dumps(
                {
                    'book_id': 'text_path_3',
                    'book_title': 'Title 3',
                    'genres': ['fiction', 'classics'],
                    'isbn': '',
                    'isbn13': '',
                    'year_first_published': '0',
                    'author': '',
                    'average_rating': '0',
                    'num_ratings': '0',
                }
            )
        )


    def test_loose_exists(self):
        self.assertTrue(loose_exists(os.path.join(EPUB_PATH, 'Another Great Title.epub')))
        # TODO: when more files generated do some more of this

    def test_compress_file(self):
        book = Book(title='t', author='a', year_published=0)
        book.set_content_location(self.clean_epub_1)
        book.tokens  # Load the tokens file

        compress_file(book.pickle_path)
        self.assertTrue(os.path.exists(book.pickle_path + '.bz'))

        content_pickle = get_file_content(book.pickle_path)
        content_bz = get_file_content(book.pickle_path + '.bz')

        self.assertEqual(content_pickle, content_bz)

        with self.assertRaises(NotImplementedError):
            compress_file(self.text_path_1)

    def test_get_metadata_goodreads(self):
        metadata = get_metadata(source='goodreads')
        expected = [
            {'book_id': 'text_path_1', 'book_title': 'Title 1', 'original_filename': '/tmp/mauve/txt/isbn___author___title1.txt', 'genres': ['fiction', 'classics'], 'isbn': '', 'isbn13': '', 'year_first_published': '0', 'author': '', 'average_rating': '0', 'num_ratings': '0'},
            {'book_id': 'text_path_2', 'book_title': 'Title 2', 'original_filename': '/tmp/mauve/txt/isbn___author___title2.txt', 'genres': ['fiction', 'classics'], 'isbn': '', 'isbn13': '', 'year_first_published': '0', 'author': '', 'average_rating': '0', 'num_ratings': '0'},
            {'book_id': 'text_path_3', 'book_title': 'Title 3', 'original_filename': '/tmp/mauve/txt/isbn___author___title3.txt', 'genres': ['fiction', 'classics'], 'isbn': '', 'isbn13': '', 'year_first_published': '0', 'author': '', 'average_rating': '0', 'num_ratings': '0'}
        ]

        metadata = sorted(metadata, key=lambda i: i['original_filename'])
        expected = sorted(expected, key=lambda i: i['original_filename'])

        print(metadata)
        print(expected)

        self.assertEqual(metadata, expected)

    def test_iter_books_goodreads(self):
        books = [b for b in iter_books()]
        self.assertEqual(len(books), 3)
        self.assertEqual(sorted([b.title for b in books]), ['Title 1', 'Title 2', 'Title 3'])