'''

To save space add this to the loop in _load_manifest in epub.py and run

Removes image files. May use them later but not for text analysis

if len(set(['.jpg', '.jpeg', '.png', '.gif', '.ttf']).intersection([ei.file_name])):
    continue
'''

import argparse
from multiprocessing import Pool
import glob
import os
import shutil

from ebooklib import epub

from mauve.constants import BASE_DATA_PATH


def remove_images(b):
    try:
        book = epub.read_epub(b)
        epub.write_epub(b+'.rmp', book)
        shutil.move(b+'.rmp', b)
    except:
        # TODO: At some point go through these
        print('NO: %s' % (b))
    else:
        print(b)


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
    for filename in glob.iglob(
        os.path.join(BASE_DATA_PATH, '**/*.epub'),
        recursive=True
    ):
        books.append(filename)

    with Pool(processes=args.num_processes) as pool:
        for processed in pool.map(
            remove_images,
            books
        ):
            print(processed)

if __name__ == '__main__':
    main()
