"""
To save space add this to the loop in _load_manifest in epub.py and run

Removes image files. May use them later but not for text analysis

if len(set(['.m4a', '.svg', '.otf', '.mp3', '.mp4', '.css', '.jpg', '.jpeg', '.png', '.gif', '.ttf']).intersection([os.path.splitext(ei.file_name)[1].lower()])):
    continue
"""

import argparse
import time
from multiprocessing import Pool
import glob
import os
import shutil

import tqdm
from ebooklib import epub

from mauve.constants import BASE_DATA_PATH


def remove_images(b):
    try:
        book = epub.read_epub(b)
        epub.write_epub(b + '.rmp', book)
        shutil.move(b + '.rmp', b)
    except Exception as ex:
        # TODO: At some point go through these
        print(ex)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=4
    )
    parser.add_argument(
        '--within-hours',
        type=int,
        dest='within_hours',
        default=24 * 365
    )
    args = parser.parse_args()

    books = []
    for filename in glob.iglob(
        os.path.join(BASE_DATA_PATH, '**/*.epub'),
        recursive=True
    ):

        if time.time() - os.path.getmtime(filename) > 60 * 60 * args.within_hours:
            continue
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
        pool.imap_unordered(remove_images, books),
        total=len(books)
    ):
        pass


if __name__ == '__main__':
    main()
