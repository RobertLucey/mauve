from unittest import TestCase
import mock

from pathlib import Path
import json
import bz2
import shutil
import glob
import os

from mauve.bin.convert_filenames import (
    clean_isbn,
    process_filenames
)

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


class TestConvertFilenames(TestCase):

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
        self.clean_epub_1 = os.path.join(CLEAN_EPUB_PATH, '9783161484101___Author A. Author___Another Great Title.epub')

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

        create_epub(  # with no / bad isbn
            isbn='1',
            title='Another Great Title',
            author='Author A. Author',
            content='blah blah blah',
            fp=os.path.join(EPUB_PATH, 'something.epub')
        )

        create_epub(  # to make sure it's skipped
            isbn='0',
            title='1',
            author='2',
            content='blah blah blah',
            fp=os.path.join(EPUB_PATH, 'something.txt')
        )


    def test_clean_isbn(self):
        self.assertFalse(os.path.exists(os.path.join(CLEAN_EPUB_PATH, '9783161484100___Author A. Author___Title title.epub')))
        self.assertTrue(os.path.exists(os.path.join(CLEAN_EPUB_PATH, '9783161484101___Author A. Author___Another Great Title.epub')))
        self.assertTrue(os.path.exists(os.path.join(CLEAN_EPUB_PATH, '9783161484101___Author A. Author___Another Great Title.epub')))

        process_filenames(num_processes=1)

        self.assertTrue(os.path.exists(os.path.join(CLEAN_EPUB_PATH, '9783161484100___Author A. Author___Title title.epub')))
        self.assertFalse(os.path.exists(os.path.join(CLEAN_EPUB_PATH, '0___1___2.epub')))

    def test_bad_epub_removed(self):
        Path(os.path.join(EPUB_PATH, 'test_bad_epub_removed.epub')).touch()

        process_filenames(num_processes=1)

        self.assertFalse(os.path.exists(os.path.join(EPUB_PATH, 'test_bad_epub_removed.epub')))
