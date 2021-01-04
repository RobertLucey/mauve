'''
Badly optimized, fight me
'''

import argparse
import os
from shutil import copyfile

from multiprocessing import Pool

from ebooklib import epub

from mauve.constants import (
    TEXT_PATH,
    EPUB_PATH,
    CLEAN_EPUB_PATH
)


def clean_isbn(isbn):
    '''
    cleaner for raw isbns strings. Should use some actual validation here.
    '''
    rm_list = [
        '-',
        'urn:uuid:',
        'urn:isbn:',
        'isbn:',
        'urn:ean:',
        'urn',
        ':isbn',
        'isbn'
    ]
    for rm_str in rm_list:
        isbn = isbn.replace(rm_str, '')

    return isbn.strip()


def process_filename(book_filename):

    if '.epub' not in book_filename:
        return

    if '___' in book_filename:
        return

    try:
        full_path = os.path.join(EPUB_PATH, book_filename)
        book = epub.read_epub(full_path)

        author = book.metadata['http://purl.org/dc/elements/1.1/']['creator'][0][0]

        real_isbn = None

        isbn = book.uid.lower().strip()
        isbn = clean_isbn(isbn)

        if len(isbn) == 13:
            real_isbn = isbn

        try:
            isbn_source = book.metadata['http://purl.org/dc/elements/1.1/']['source'][0][0]
            isbn = clean_isbn(isbn_source)

            if len(isbn_source) == 13:
                real_isbn = isbn_source
        except:
            pass

        try:
            isbn_identifier = book.metadata['http://purl.org/dc/elements/1.1/']['identifier'][0][1]['id'].replace('p', '')

            if len(isbn_identifier) == 13:
                real_isbn = isbn_identifier
        except:
            pass

        try:
            isbn_identifier_2 = book.metadata['http://purl.org/dc/elements/1.1/']['identifier'][1][0]

            if len(isbn_identifier_2) == 13:
                real_isbn = isbn_identifier_2
        except:
            pass

        if real_isbn is None:
            return

        # TODO: validate the isbn, there's some cruft in here

        new_path = os.path.join(
            CLEAN_EPUB_PATH,
            '%s___%s___%s.epub' % (
                real_isbn,
                author,
                book.title
            )
        )

        if os.path.exists(new_path):
            return

        print('%s -> %s' % (full_path, new_path))

        copyfile(full_path, new_path)
    except epub.EpubException:
        print('Bad file: remove %s' % (full_path))
        os.remove(full_path)
    except:
        print('No: %s' % (book_filename))
    else:
        print('Good: %s' % (book_filename))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=4
    )
    args = parser.parse_args()

    res = []
    with Pool(processes=args.num_processes) as pool:
        res.extend(
            pool.map(
                process_filename,
                os.listdir(EPUB_PATH)
            )
        )


if __name__ == '__main__':
    main()
