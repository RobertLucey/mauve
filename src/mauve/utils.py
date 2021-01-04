import os
import random
import json

import fast_json

from mauve.models.book import Book
from mauve.models.tag import Tags, Tag
from mauve.constants import SIMPLE_TOKEN_MAP


def get_metadata(data_dir, version=1):
    '''

    :param data_dir:
    :kwarg version:
    :return:
    :rtype:
    '''
    data = []

    title_id_map = fast_json.loads(
        open(os.path.join(data_dir, 'title_id_map.json'), 'r').read()
    )

    filenames = os.listdir(data_dir)
    random.shuffle(filenames)

    if version == 1:
        filenames = [f for f in filenames if '.v2' in f]
    elif version == 2:
        filenames = [f for f in filenames if '.v2' not in f]  # fix

    for filename in filenames:
        if filename == 'title_id_map.json':
            continue
        try:
            tmp = fast_json.loads(
                open(os.path.join(data_dir, filename), 'r').read()
            )
            real_filename = title_id_map[tmp['book_id']]
            tmp['original_filename'] = real_filename
            data.append(tmp)
        except:
            print('Problematic file: %s' % (filename))

    return data


def iter_books(data_dir, books_dir, version=1):
    '''

    :param data_dir:
    :param books_dir:
    :kwarg: the v of tokens to get from
    :return: generator of book objects
    '''
    for book_meta in get_metadata(data_dir, version=version):
        content_path = os.path.join(
            books_dir,
            book_meta['original_filename']
        )

        genres = book_meta['genres']

        tags = Tags()
        for g in genres:
            tags.append(Tag(name=g))

        book = Book(
            title=book_meta['book_title'],
            isbn=book_meta['isbn'],
            isbn13=book_meta['isbn13'],
            year_published=book_meta['year_first_published'],
            author=book_meta['author'],
            avg_rating=book_meta['average_rating'],
            tags=tags,
            num_ratings=book_meta['num_ratings']
        )

        book.set_content_location(content_path)

        yield book
