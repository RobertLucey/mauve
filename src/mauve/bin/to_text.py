import argparse
import os
from multiprocessing import Pool

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

from mauve.constants import (
    TEXT_PATH,
    CLEAN_EPUB_PATH
)


blacklist = [
    '[document]',
    'noscript',
    'header',
    'html',
    'meta',
    'head',
    'input',
    'script'
]


def epub2thtml(epub_path):
    chapters = []
    for item in epub.read_epub(epub_path).get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_content())
    return chapters


def epub2text(epub_path):
    chapters = epub2thtml(epub_path)
    ttext = thtml2ttext(chapters)
    return ttext


def thtml2ttext(thtml):
    output = []
    for html in thtml:
        text = chap2text(html)
        output.append(text)
    return output


def chap2text(chap):
    output = ''
    soup = BeautifulSoup(chap, 'html.parser')
    text = soup.find_all(text=True)
    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)
    return output


def process(book_path):

    full_path = os.path.join(CLEAN_EPUB_PATH, book_path)
    text_path = os.path.join(TEXT_PATH, book_path.replace('.epub', '.txt'))

    if os.path.exists(text_path):
        return

    try:
        out = epub2text(full_path)
        f = open(text_path, 'w')
        f.write('\n'.join(out))
        f.close()
        print(text_path)
    except:
        pass


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
                process,
                os.listdir(CLEAN_EPUB_PATH)
            )
        )


if __name__ == '__main__':
    main()
