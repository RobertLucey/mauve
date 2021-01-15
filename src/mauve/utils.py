import os
import random
import pickle

import fast_json
from compress_pickle import (
    dump,
    load
)

from mauve.models.book import Book
from mauve.models.tag import (
    Tag,
    Tags
)
from mauve.constants import (
    GOODREADS_METADATA_PATH,
    SIMPLE_TOKEN_MAP
)


def loose_exists(fp):
    return get_loose_filepath(fp) is not None


def get_loose_filepath(fp):
    ext = os.path.splitext(fp)[1]
    pass
    # always see first
    # if bz remove and see
    # if pickle add bz and see


def compress_file(fp):
    ext = os.path.splitext(fp)[1]
    if ext == '.txt':
        # We want to do this? txt files necessary at all?
        raise NotImplementedError()
    elif ext == '.pickle':
        return dump(
            get_file_content(fp),
            fp,
            compression='bz2'
        )
    elif ext == 'bz2':
        pass
    else:
        raise NotImplementedError()


def get_file_content(fp):
    '''

    :param fp:
    :return:
    '''
    ext = os.path.splitext(fp)[1]
    if ext == '.txt':
        return open(fp, 'r').read()
    elif ext == '.pickle':
        return pickle.load(open(fp, 'rb'))
    elif ext == '.bz':
        return load(os.path.splitext(fp)[0], 'bz2')
    else:
        raise NotImplementedError()


def get_metadata(source='goodreads', version=1):
    '''

    :param data_dir:
    :kwarg source:
    :kwarg version:
    :return:
    :rtype:
    '''
    data = []
    if source == 'goodreads':
        data_dir = GOODREADS_METADATA_PATH
    else:
        raise Exception('No source named %s' % (source))

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


def iter_books(books_dir, source='goodreads', version=1):
    '''

    :param data_dir:
    :param books_dir:
    :kwarg source:
    :kwarg: the v of tokens to get from
    :return: generator of book objects
    '''
    for book_meta in get_metadata(source=source, version=version):
        content_path = os.path.join(
            books_dir,
            book_meta['original_filename']
        )

        genres = book_meta['genres']

        tags = Tags()
        for genre in genres:
            tags.append(Tag(name=genre))

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
