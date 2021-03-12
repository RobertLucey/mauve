from unittest import TestCase
import mock

from pathlib import Path
import json
import bz2
import shutil
import glob
import os

from mauve.bin.load_tokens import process_filenames

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

        self.text_path_1 = os.path.join(TEXT_PATH, 'isbn___author___title1.txt')
        self.text_path_2 = os.path.join(TEXT_PATH, 'isbn___author___title2.txt')
        self.text_path_3 = os.path.join(TEXT_PATH, 'isbn___author___title3.txt')

        self.write(self.text_path_1, 'blah blah blah')
        self.write(self.text_path_2, 'blah blah blah')
        self.write(self.text_path_3, 'blah blah blah')

    def test_compress_files(self):
        process_filenames(num_processes=1)

        self.assertTrue(os.path.exists(self.text_path_1 + '.all_tokenv2.pickle'))
        self.assertTrue(os.path.exists(self.text_path_2 + '.all_tokenv2.pickle'))
        self.assertTrue(os.path.exists(self.text_path_3 + '.all_tokenv2.pickle'))

        self.assertTrue(os.path.exists(self.text_path_1 + '.word_tokenv2.pickle'))
        self.assertTrue(os.path.exists(self.text_path_2 + '.word_tokenv2.pickle'))
        self.assertTrue(os.path.exists(self.text_path_3 + '.word_tokenv2.pickle'))

        content = get_file_content(self.text_path_1 + '.all_tokenv2.pickle')
        self.assertEquals(content, [('blah', 'NN'), ('blah', 'NN'), ('blah', 'NN')])
