from unittest import TestCase
import mock

from pathlib import Path
import json
import bz2
import shutil
import glob
import os

from mauve.bin.to_text import process_files

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


class TestCompressFiles(TestCase):

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

    def test_to_text_creation(self):
        process_files(num_processes=1)

        self.assertTrue(
            os.path.exists(
                os.path.join(TEXT_PATH, '9783161484102___Author A. Author___Another Great Title.txt')
            )
        )

    def test_to_text_content(self):
        process_files(num_processes=1)

        content = get_file_content(os.path.join(TEXT_PATH, '9783161484102___Author A. Author___Another Great Title.txt'))
        self.assertEquals(
            content,
            '''Intro heading 
 blah blah blah 
 

 Another Great Title 
 
 
 Introduction 
 
 
 Simple book 
 
 
 Intro 
 
 
 
 
 
 '''
        )
