"""
Use this to set the tokens of books.
Just set the data dir for output and the source txt dir
"""

import argparse
import os
from multiprocessing import Pool

import tqdm

from mauve.utils import iter_books


def get_tokens(b):
    b.all_tokens
    b.word_tokens

    return b.title


def process_filenames(num_processes=4):
    files = []
    for i in iter_books(source='local_text'):

        all_set = os.path.exists(i.all_tokens_pickle_path + '.bz') or os.path.exists(i.all_tokens_pickle_path) or '.all_tokenv' in i.content_path
        word_set = os.path.exists(i.word_tokens_pickle_path + '.bz') or os.path.exists(i.word_tokens_pickle_path) or '.word_tokenv' in i.content_path

        if all_set and word_set:
            continue

        files.append(i)

    if num_processes == 1:
        for f in files:
            get_tokens(f)
    else:  # pragma: nocover
        pool = Pool(processes=num_processes)
        for _ in tqdm.tqdm(
            pool.imap_unordered(get_tokens, files),
            total=len(files)
        ):
            pass


def main():  # pragma: nocover

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=1
    )
    args = parser.parse_args()

    process_filenames(num_processes=args.num_processes)


if __name__ == '__main__':  # pragma: nocover
    main()
