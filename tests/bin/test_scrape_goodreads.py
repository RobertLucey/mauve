from pathlib import Path
import shutil

from unittest import TestCase
import mock

from mauve.constants import (
    TEXT_PATH,
    EPUB_PATH,
    CLEAN_EPUB_PATH,
    OIREACHTAS_DIR,
    GOODREADS_METADATA_PATH
)

from mauve.bin.scrape_goodreads import (
    get_title_id_cache,
    get_request_chunk_items,
    write_title_id_cache,
    write_book_metadata
)


class TestScrapeGoodreads(TestCase):

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

    def test_get_title_id_cache(self):
        # TODO: check the data, make sure it fails if it's bad
        data = {'1': 'A Book', '2': 'A Book: The Sequel'}
        write_title_id_cache(data)
        self.assertEqual(
            get_title_id_cache(),
            data
        )

    def test_get_request_chunk_items(self):
        # TODO: check the data, make sure it fails if it's bad
        title_id_cache = {'1': 'A Book', '2': 'A Book: The Sequel'}
        files = ['1___Me___A Book.txt', '2___Me___A Book: The Sequel.txt']
        self.assertEqual(
            get_request_chunk_items(files, title_id_cache),
            [
                {
                    'title': 'A Book',
                    'original_filename': '1___Me___A Book.txt',
                    'isbn': '1'
                },
                {
                    'title': 'A Book: The Sequel',
                    'original_filename': '2___Me___A Book -  The Sequel.txt',
                    'isbn': '2'
                }
            ]
        )

    def test_write_title_id_cache(self):
        # TODO: check the data, make sure it fails if it's bad
        write_title_id_cache({'1': 'A Book', '2': 'A Book: The Sequel'})

    def test_write_book_metadata(self):
        # TODO: check the data, make sure it fails if it's bad
        metadata = [
            {
                'book_id': '1',
                'book_title': 'A Book',
                'isbn': 'isbn',
                'isbn13': 'isbn13',
                'year_first_published': 2000,
                'author': 'me',
                'num_pages': 1,
                'genres': ['nonfiction', 'history'],
                'num_ratings': 100,
                'num_reviews': 10,
                'average_rating': 5.0,
                'rating_distribution': {
                    '5 Stars': 100,
                    '4 Stars': 0,
                    '3 Stars': 0,
                    '2 Stars': 0,
                    '1 Stars': 0,
                }
            }
        ]
        write_book_metadata(metadata)
