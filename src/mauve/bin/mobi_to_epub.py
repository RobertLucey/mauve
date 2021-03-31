import argparse
import os
from multiprocessing import Pool
import glob

import tqdm

from mauve.constants import BASE_DATA_PATH


def to_epub(book_path):
    os.system(
        '/usr/bin/ebook-convert "%s" "%s" > /dev/null' % (
            book_path,
            book_path.replace('.mobi', '.epub')
        )
    )
    os.remove(book_path)


def mobi_to_epub(num_processes=1):

    books = []
    for filename in glob.iglob(
        os.path.join(BASE_DATA_PATH, '**/*.mobi'),
        recursive=True
    ):
        books.append(filename)

    if num_processes == 1:
        for book_path in books:
            to_epub(book_path)
    else:  # pragma: nocover
        pool = Pool(processes=num_processes)
        for _ in tqdm.tqdm(
            pool.imap_unordered(to_epub, books),
            total=len(books)
        ):
            pass


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=7
    )
    args = parser.parse_args()

    mobi_to_epub(num_processes=args.num_processes)


if __name__ == '__main__':  # pragma: nocover
    main()
