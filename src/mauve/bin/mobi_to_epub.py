import argparse
import os
from multiprocessing import Pool
import subprocess
import glob

import tqdm

from mauve.utils import iter_books

from mauve.constants import BASE_DATA_PATH


def to_epub(b):
    os.system('/usr/bin/ebook-convert "%s" "%s" > /dev/null' % (b, b.replace('.mobi', '.epub')))
    os.remove(b)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=7
    )
    args = parser.parse_args()

    books = []
    for filename in glob.iglob(
        os.path.join(BASE_DATA_PATH, '**/*.mobi'),
        recursive=True
    ):
        books.append(filename)

    pool = Pool(processes=args.num_processes)
    for _ in tqdm.tqdm(
        pool.imap_unordered(to_epub, books),
        total=len(books)
    ):
        pass


if __name__ == '__main__':
    main()
