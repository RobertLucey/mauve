import argparse
import os
from multiprocessing import Pool

import tqdm

from mauve.utils import iter_books

from mauve.constants import (
    TEXT_PATH,
    GOODREADS_METADATA_PATH,
    TOKEN_VERSION
)


def get_tokens(b):
    try:
        b.push_to_splunk()
        del b
    except Exception as ex:
        print('BAD: %s %s' (b.title, ex))
        pass


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
    for i in iter_books(source='local_text'):
        if os.path.exists(i.content_path + '.tokenv{}.pickle'.format(TOKEN_VERSION)):
            books.append(i)

    pool = Pool(processes=args.num_processes)
    for _ in tqdm.tqdm(
        pool.imap_unordered(get_tokens, books),
        total=len(books)
    ):
        pass

if __name__ == '__main__':
    main()
