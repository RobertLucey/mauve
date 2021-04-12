import json
import uuid
import os

from ebooklib import epub

from mauve import constants
from mauve.constants import (
    TEXT_PATH,
    EPUB_PATH,
    CLEAN_EPUB_PATH,
    OIREACHTAS_DIR,
    TOKEN_VERSION,
    GOODREADS_METADATA_PATH
)


def create_epub(isbn=None, title=None, author=None, content='blah blah blah', fp=None):

    book = epub.EpubBook()

    # set metadata
    book.set_identifier(isbn)
    book.set_title(title)
    book.set_language('en')

    book.add_author(author)

    # create chapter
    c1 = epub.EpubHtml(title='Intro', file_name='chap_01.xhtml', lang='hr')
    c1.content = '<h1>Intro heading</h1><p>' + content + '</p>'

    # add chapter
    book.add_item(c1)

    # define Table Of Contents
    book.toc = (
        epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
        (
            epub.Section('Simple book'),
            (c1, )
        )
    )

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define CSS style
    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(
        uid='style_nav',
        file_name='style/nav.css',
        media_type='text/css',
        content=style
    )

    # add CSS file
    book.add_item(nav_css)

    # basic spine
    book.spine = ['nav', c1]

    # write to the file
    epub.write_epub(fp, book, {})



def write(fp, content):
    f = open(fp, 'w')
    f.write(content)
    f.close()


def write_book(title, author, content, isbn='isbn', nationality='Ireland', author_birth=1994):
    text_path = os.path.join(TEXT_PATH, 'isbn___{}___{}.txt'.format(author, title))
    write(text_path, content)

    goodreads_id = uuid.uuid4()

    if os.path.exists(constants.TITLE_ID_MAP_PATH):
        data = None
        with open(constants.TITLE_ID_MAP_PATH, 'r') as outfile:
            data = json.load(outfile)
        data[str(goodreads_id)] = os.path.join(TEXT_PATH, 'isbn___{}___{}.txt'.format(author, title))
        with open(constants.TITLE_ID_MAP_PATH, 'w') as outfile:
            json.dump(data, outfile)
    else:
        data = {
            str(goodreads_id): os.path.join(TEXT_PATH, 'isbn___{}___{}.txt'.format(author, title))
        }
        with open(constants.TITLE_ID_MAP_PATH, 'w') as outfile:
            json.dump(data, outfile)


    if os.path.exists(constants.AUTHOR_METADATA_PATH):
        data = None
        with open(constants.AUTHOR_METADATA_PATH, 'r') as outfile:
            data = json.load(outfile)
        data[author] = {
            'born': author_birth,
            'nationality': nationality
        }
        with open(constants.AUTHOR_METADATA_PATH, 'w') as outfile:
            json.dump(data, outfile)
    else:
        data = {
            author: {
                'born': author_birth,
                'nationality': nationality
            }
        }
        with open(constants.AUTHOR_METADATA_PATH, 'w') as outfile:
            json.dump(data, outfile)

    constants.AUTHOR_METADATA = data

    with open('/tmp/mauve/metadata/{}.json'.format(str(goodreads_id)), 'w') as outfile:
        json.dump(
            {
                'book_id': str(goodreads_id),
                'book_title': title,
                'isbn': isbn,
                'year_first_published': '2010',
                'author': author,
                'genres': ['classics', 'fiction'],
                'num_ratings': '288992',
                'num_reviews': '10058',
                'average_rating': '3.86',
                'rating_distribution': {'5 Stars': 86206, '4 Stars': 105449, '3 Stars': 73871, '2 Stars': 18111, '1 Star': 5355}
            },
            outfile
        )
