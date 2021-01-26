import os
import random
import pickle
from functools import lru_cache

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import PorterStemmer
import fast_json
from compress_pickle import (
    dump,
    load
)

from mauve.models.books.tag import (
    Tag,
    Tags
)
from mauve.constants import (
    GOODREADS_METADATA_PATH,
    SIMPLE_TOKEN_MAP,
    TEXT_PATH
)


STEMMER = PorterStemmer()
LEM = WordNetLemmatizer()


def loose_exists(filepath):
    '''

    :param filepath: filepath to get a related file of
    :return: Bool if a file or related file exists
    '''
    return get_loose_filepath(filepath) is not None


def get_loose_filepath(filepath):
    '''

    :param: filepath to get a related file of
    :return: The path to the file or loose file that was found
    '''
    if os.path.exists(filepath):
        return filepath

    ext = os.path.splitext(filepath)[1]
    if ext == '.bz':
        unextend = os.path.splitext(filepath)[0]
        if os.path.exists(unextend):
            return unextend
    elif ext == '.pickle':
        if os.path.exists(filepath + '.bz'):
            return filepath
    elif ext == '.txt':
        if os.path.exists(filepath + '.bz'):
            return filepath
        if os.path.exists(filepath + '.pickle'):
            return filepath

    return None


def compress_file(filepath):
    '''
    Compress a file if possible. When reading files that may have been
    compressed use the get_file_content

    :param filepath: Filepath to compress
    '''
    ext = os.path.splitext(filepath)[1]
    if ext == '.txt':
        # We want to do this? txt files necessary at all?
        raise NotImplementedError()
    elif ext == '.pickle':
        return dump(
            get_file_content(filepath),
            filepath,
            compression='bz2'
        )
    elif ext == 'bz2':
        pass
    else:
        raise NotImplementedError()


def get_file_content(filepath):
    '''
    Read a file regardless of the extension

    For instance if there's some pickle files and some pickle.bz files
    this will give back the same data as if they were not compressed

    :param filepath: Filepath to read from
    :return: Depending on the ext it may be a pickled obj / str
    '''
    ext = os.path.splitext(filepath)[1]
    if ext == '.txt':
        return open(filepath, 'r').read()
    elif ext == '.pickle':
        return pickle.load(open(filepath, 'rb'))
    elif ext == '.bz':
        return load(os.path.splitext(filepath)[0], 'bz2')
    else:
        raise NotImplementedError()


def get_metadata(source='goodreads'):
    '''

    :kwarg source: The type of source to get metadata from
    :return: All metadata related to whatever books you're looking for
    :rtype: list
    '''
    data = []
    if source == 'goodreads':
        data_dir = GOODREADS_METADATA_PATH

        title_id_map = fast_json.loads(
            open(os.path.join(data_dir, 'title_id_map.json'), 'r').read()
        )

        filenames = os.listdir(data_dir)
        random.shuffle(filenames)

        for filename in filenames:
            if filename == 'title_id_map.json':
                continue
            ext = os.path.splitext(filename)[1]
            if ext != '.json':
                continue
            try:
                tmp = fast_json.loads(
                    open(os.path.join(data_dir, filename), 'r').read()
                )
                real_filename = title_id_map[tmp['book_id']]
                tmp['original_filename'] = real_filename
                data.append(tmp)
            except Exception as ex:
                print('Problematic file: %s %s' % (filename, ex))
    elif source == 'local_text':
        data_dir = TEXT_PATH

        filenames = os.listdir(data_dir)
        random.shuffle(filenames)

        for filename in filenames:
            data.append(
                {
                    'original_filename': os.path.join(data_dir, filename)
                }
            )
    else:
        raise Exception('No source named %s' % (source))

    return data


def iter_books(source='goodreads'):
    '''

    :param books_dir:
    :kwarg source:
    :kwarg: the v of tokens to get from
    :return: generator of book objects
    '''
    from mauve.models.books.book import Book
    books_dir = {
        'goodreads': GOODREADS_METADATA_PATH,
        'local_text': TEXT_PATH
    }[source]
    for book_meta in get_metadata(source=source):
        content_path = os.path.join(
            books_dir,
            book_meta['original_filename']
        )

        genres = book_meta.get('genres', [])

        tags = Tags()
        for genre in genres:
            tags.append(Tag(name=genre))

        book = Book(
            title=book_meta.get('book_title', None),
            isbn=book_meta.get('isbn', None),
            isbn13=book_meta.get('isbn13', None),
            year_published=book_meta.get('year_first_published', None),
            author=book_meta.get('author', None),
            avg_rating=book_meta.get('average_rating', None),
            tags=tags,
            num_ratings=book_meta.get('num_ratings', None)
        )

        book.set_content_location(content_path)

        yield book


@lru_cache(maxsize=100000)
def get_stem(word):
    return STEMMER.stem(word)


@lru_cache(maxsize=100000)
def get_lem(word, pos=None):
    return LEM.lemmatize(word, pos)


def lower(x):
    try:
        return x.lower()
    except:
        pass


def find_sub_idx(test_list, repl_list, start=0):
    length = len(repl_list)
    for idx in range(start, len(test_list)):
        if test_list[idx:idx + length] == repl_list:
            return idx, idx + length


def replace_sub(test_list, repl_list, new_list):
    length = len(new_list)
    idx = 0
    for start, end in iter(lambda: find_sub_idx(test_list, repl_list, idx), None):
        test_list[start:end] = new_list
        idx = start + length
    return test_list


def previous_current_next(iterable):
    '''
    Make an iterator that yields an (previous, current, next) tuple per element.

    Returns None if the value does not make sense (i.e. previous before
    first and next after last).
    '''
    iterable = iter(iterable)
    prv = None
    cur = iterable.__next__()
    try:
        while True:
            nxt = iterable.__next__()
            yield (prv, cur, nxt)
            prv = cur
            cur = nxt
    except StopIteration:
        yield (prv, cur, None)
