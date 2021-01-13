'''
Badly optimized, fight me
'''

import glob
import argparse
import os
from shutil import copyfile
from multiprocessing import Pool

import tqdm
from ebooklib import epub

from mauve.constants import (
    BASE_DATA_PATH,
    TEXT_PATH,
    EPUB_PATH,
    CLEAN_EPUB_PATH
)
from mauve.utils import (
    compress_file,
    get_file_content
)

from compress_pickle import (
    dump,
    load
)

def _compress_file(fp):
    if os.path.exists(fp + '.bz'):
        os.remove(fp)
    else:
        compress_file(fp)
        os.remove(fp)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=6
    )
    args = parser.parse_args()

    books = []
    #for filename in glob.iglob(
    #    os.path.join(BASE_DATA_PATH, '**/*.txt'),
    #    recursive=True
    #):
    #    books.append((filename, os.path.getsize(filename)))

    for filename in glob.iglob(
        os.path.join(BASE_DATA_PATH, '**/*.pickle'),
        recursive=True
    ):
        books.append((filename, os.path.getsize(filename)))

    books = [
        b[0] for b in sorted(
            books,
            key=lambda tup: tup[1],
            reverse=True
        )
    ]

    pool = Pool(processes=args.num_processes)
    for _ in tqdm.tqdm(
        pool.imap_unordered(_compress_file, books),
        total=len(books)
    ):
        pass

if __name__ == '__main__':
    main()
