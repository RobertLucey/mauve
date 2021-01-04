'''
Use this to set the tokens of books.
Just set the data dir for output and the source txt dir
'''

import argparse
import os
from multiprocessing import Pool

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
        if os.path.exists(i.content_path + '.tokenv2.json'):
            continue
        books.append(i)

    with Pool(processes=args.num_processes) as pool:
        for processed in pool.map(
            get_tokens,
            books
        ):
            print(processed)


if __name__ == '__main__':
    main()
