from unittest import TestCase
import mock

from pathlib import Path
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
    TOKEN_VERSION
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

        self.write(os.path.join(TEXT_PATH, 'isbn___author___title1.txt'), 'blah blah blah')
        self.write(os.path.join(TEXT_PATH, 'isbn___author___title2.txt'), 'blah blah blah')
        self.write(os.path.join(TEXT_PATH, 'isbn___author___title3.txt'), 'blah blah blah')

        # a dirty epub
        create_epub(
            isbn='978-3-16-148410-0',
            title='Title title',
            author='Author A. Author',
            content='blah blah blah',
            fp=os.path.join(EPUB_PATH, 'Title Title.epub')
        )

        # a dirty epub
        create_epub(
            isbn='978-3-16-148410-0',
            title='Another Great Title',
            author='Author A. Author',
            content='blah blah blah',
            fp=os.path.join(EPUB_PATH, 'Another Great Title.epub')
        )

        # a cleaned dirty epub (Title Title)
        create_epub(
            isbn='978-3-16-148410-0',
            title='Another Great Title',
            author='Author A. Author',
            content='blah blah blah',
            fp=os.path.join(CLEAN_EPUB_PATH, '9783161484100___Author A. Author___Another Great Title.epub')
        )


    def test_loose_exists(self):
        self.assertTrue(loose_exists(os.path.join(EPUB_PATH, 'Another Great Title.epub')))
        # TODO: when more files generated do some more of this

    def test_compress_file(self):
        book = Book(title='t', author='a', year_published=0)
        book.set_content_location(os.path.join(CLEAN_EPUB_PATH, '9783161484100___Author A. Author___Another Great Title.epub'))
        book.tokens  # Load the tokens file

        compress_file(book.pickle_path)
        self.assertTrue(os.path.exists(book.pickle_path + '.bz'))

        content_pickle = get_file_content(book.pickle_path)
        content_bz = get_file_content(book.pickle_path + '.bz')

        self.assertEqual(content_pickle, content_bz)
