from unittest import TestCase
import mock

from pathlib import Path
import json
import bz2
import shutil
import glob
import os

from mauve.analyse.word_usage_by_group import AuthorGenderWordUsage

from mauve.models.books.book import Book
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

from ..utils import create_epub


class TestWordCountsByGroup(TestCase):

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

        self.text_path_1 = os.path.join(TEXT_PATH, 'isbn___Alice___title1.txt')
        self.text_path_2 = os.path.join(TEXT_PATH, 'isbn___Bob___title2.txt')
        self.text_path_3 = os.path.join(TEXT_PATH, 'isbn___Bob___title3.txt')

        self.write(self.text_path_1, 'this is a book: female')
        self.write(self.text_path_2, 'this is a book: male')
        self.write(self.text_path_3, 'this is a book: male')

        # a dirty epub
        create_epub(
            isbn='978-3-16-148410-0',
            title='Title title',
            author='Alice',
            content='female',
            fp=self.dirty_epub_1
        )

        # a dirty epub
        create_epub(
            isbn='978-3-16-148410-1',
            title='Another Great Title',
            author='Bob',
            content='male male',
            fp=self.dirty_epub_2
        )

        # a cleaned dirty epub (Title Title)
        create_epub(
            isbn='978-3-16-148410-2',
            title='Another Great Title',
            author='Bob',
            content='male',
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
                    'year_first_published': '2000',
                    'author': 'Alice',
                    'average_rating': '0',
                    'num_ratings': '100',
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
                    'year_first_published': '2000',
                    'author': 'Bob',
                    'average_rating': '0',
                    'num_ratings': '100',
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
                    'year_first_published': '2000',
                    'author': 'Bob',
                    'average_rating': '0',
                    'num_ratings': '100',
                }
            )
        )

    def test_gender_word_usage(self):
        gender_word_usage = AuthorGenderWordUsage(
            method='by_word',
            required_genre='fiction',
            required_lang='en',
            required_safe_to_use=True
        )
        gender_word_usage.process()
        self.assertEqual(
            [
                ('female', 'male', ['female', 'book', 'male']),
                ('male', 'female', ['male', 'book', 'female'])
            ],
            sorted(
                gender_word_usage.get_stats(),
                key=lambda item: item[0]
            )
        )
