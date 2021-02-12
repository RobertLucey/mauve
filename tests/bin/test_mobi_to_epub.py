from unittest import TestCase
import mock

import os
from shutil import copyfile
from pathlib import Path
import json
import bz2
import shutil
import glob
import os

from mauve.bin.mobi_to_epub import mobi_to_epub
from mauve.bin.to_text import process_files as to_text

from mauve.constants import CLEAN_EPUB_PATH, TEXT_PATH


RESOURCE_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    ),
    'tests/resources'
)


class TestMobiToEpub(TestCase):

    def setUp(self):
        try:
            shutil.rmtree('/tmp/mauve')
        except:
            pass

        Path(CLEAN_EPUB_PATH).mkdir(parents=True, exist_ok=True)
        Path(TEXT_PATH).mkdir(parents=True, exist_ok=True)

        self.resource_alice_mobi = os.path.join(RESOURCE_PATH, 'alices_adventures_in_wonderland.mobi')
        self.alice_mobi_path = os.path.join(CLEAN_EPUB_PATH, 'alice.mobi')

        copyfile(self.resource_alice_mobi, self.alice_mobi_path)

    def test_mobi_to_epub(self):
        mobi_to_epub()
        to_text()
        content = open(os.path.join(TEXT_PATH, 'alice.txt')).read()
        self.assertTrue('Do cats eat bats?' in content)
