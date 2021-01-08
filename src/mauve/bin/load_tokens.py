'''
Use this to set the tokens of books.
Just set the data dir for output and the source txt dir
'''

import argparse
import os
from multiprocessing import Pool

import tqdm

from mauve.utils import iter_books

from mauve.constants import (
    TEXT_PATH,
    GOODREADS_METADATA_PATH
)


def get_tokens(b):
    b.tokens
    return b.title


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=4
    )
    args = parser.parse_args()

    books = []
    for i in iter_books(GOODREADS_METADATA_PATH, TEXT_PATH, version=2):
        if os.path.exists(i.content_path + '.tokenv2.pickle'):
            continue
        books.append(i)

    pool = Pool(processes=args.num_processes)
    for _ in tqdm.tqdm(
        pool.imap_unordered(get_tokens, books),
        total=len(books)
    ):
        pass

if __name__ == '__main__':
    main()
