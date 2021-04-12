import copy
import uuid
import json
import os

from unittest import TestCase

from gensim.models import Doc2Vec

from mauve import constants
from mauve.learn.tagged_docs import (
    AuthorTaggedDocs,
    GenderTaggedDocs,
    AuthorTaggedDocs
)

from mauve.learn.generate import ClassifierCreator

from pathlib import Path
import shutil

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

from ..utils import write_book


class TestBaseTaggedDocs(TestCase):

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

        content = 'this is a sentence in english. two two two two' * 100
        content_2 = 'this is some other sentence in english. one one one one' * 100

        for i in range(10):
            write_book('title %s' % (i,), 'someone', content)
            write_book('title %s' % (i,), 'someone 2', content_2)

    def test_load(self):

        classifier_creator = ClassifierCreator(
            Doc2Vec(
                min_count=5,
                window=10,
                vector_size=150,
                sample=1e-4,
                negative=5,
                workers=7
            ),
            AuthorTaggedDocs(
                min_per_group=5
            ),
            num_items=10000
        )

        classifier_creator.generate_classifier()

        content = 'this is a sentence in english. two two two two' * 100
        content_2 = 'this is some other sentence in english. one one one one' * 100

        self.assertEqual(
            classifier_creator.predict(content),
            'someone'
        )
        self.assertEqual(
            classifier_creator.predict(content_2),
            'someone 2'
        )
