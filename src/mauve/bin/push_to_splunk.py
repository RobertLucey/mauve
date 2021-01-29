import argparse
import os
from multiprocessing import Pool

import tqdm

from mauve.constants import (
    TOKEN_VERSION
)
from mauve.utils import iter_books


def push_to_splunk(b):
    try:
        b.push_to_splunk()
        del b
    except Exception as ex:
        print('BAD: %s %s' (b.title, ex))
        pass


def process_files(num_processes=4):
    files = []
    for i in iter_books(source='local_text'):
        if os.path.exists(i.content_path + '.tokenv{}.pickle'.format(TOKEN_VERSION)):
            files.append(i)

    if num_processes == 1:
        for f in files:
            push_to_splunk(f)
    else:  # pragma: nocover
        pool = Pool(processes=num_processes)
        for _ in tqdm.tqdm(
            pool.imap_unordered(push_to_splunk, files),
            total=len(files)
        ):
            pass


def main():  # pragma: nocover

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=4
    )
    args = parser.parse_args()

    process_files(num_processes=args.num_processes)


if __name__ == '__main__':  # pragma: nocover
    main()
