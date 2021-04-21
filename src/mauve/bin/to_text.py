import argparse
import logging
import os
from multiprocessing import Pool
import re

import tqdm
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

from mauve.constants import (
    TEXT_PATH,
    CLEAN_EPUB_PATH
)

logger = logging.getLogger('mauve')

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

ignore_files = {'foreword', 'epigraph', 'dedication', 'title', 'cover', 'copyright', 'legal', 'toc', 'nav', 'alsoby', 'author', 'contents', 'index', 'excerpt', 'acknowledgements', 'backcovertext', 'praise', 'titlepage', 'preface', 'abouttheauthor', 'review', 'ack', 'ded', 'cop', 'prf', 'back', 'page-template', 'footnote', 'about_publisher', 'navdoc', 'next-reads', 'about_book', 'about_author', 'bio', 'keepreading', 'about_the_author', 'about_the_publisher', 'introduction', 'also', 'coverimage', 'notes', 'coverpage', 'epi', 'navigation', 'epilogue', 'glossary', 'further', 'appendix', 'front', 'note', 'intro', 'glossary', 'bibliography', 'aboutthepublisher', 'afterword', 'acknowledgements', 'authorsnote', 'bib', 'blurb', 'personblurb', 'ad-card', 'welcome', 'listofillustrations', 'acknowledgments', 'prologue', 'halftitle', 'also_by', 'frontmatter', 'conclusion', 'acknow', 'fm', 'bm', 'copy', 'backcover', 'title_page', 'summary', 'cov', 'frontcover', 'contribute', 'tableofcontents', 'bythesameauthor', 'booktitlepage', 'aboutpublisher', 'authorbio', 'backadd', 'copyright-page', 'information', 'credits', 'endnotes', 'globalbackad', 'suggestions', 'references', 'references', 'advance', 'abouttheeditor', 'aboutauthor', 'introd', 'epilog', 'foot', 'references', 'halftitlepage', 'glossary-and-abbreviations', 'table_of_contents', 'biographies', 'backmatter', 'biography', 'acknowledgmentpage', 'aboutauthorpage', 'copyrightpage', 'epiloguepage', 'prologuepage', 'acknowledgment', 'half_title', 'aut', 'booksby', 'about', 'appen'}

ignore_file_startswith = {'appendix', 'footnote', 'dedication', 'toc', 'frontmatter', 'foreward', 'afterword', 'preface'}


def epub2thtml(epub_path):
    chapters = []
    for item in epub.read_epub(epub_path).get_items():
        fn = os.path.splitext(os.path.basename(item.file_name))[0].lower().replace(' ', '_')
        ext = os.path.splitext(item.file_name)[-1]

        # footnote can be footnote1 etc
        # remove the isbn from the fn

        if ext not in {'.htm', '.html', '.xhtml'}:
            continue

        if re.match(r'^\d+_\w+', fn) is not None:
            fn = '_'.join(fn.split('_')[1:])
        if re.match(r'^\d+-\w+', fn) is not None:
            fn = '-'.join(fn.split('_')[1:])

        if fn in ignore_files:
            continue

        if any([fn.startswith(pre) for pre in ignore_file_startswith]):
            continue

        logger.debug('Including file: %s', fn)

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
    text_path = os.path.join(TEXT_PATH, book_path.replace('.epub', '.txt'))  # already clean

    if os.path.exists(text_path):
        return

    try:
        out = epub2text(full_path)
        f = open(text_path, 'w')
        f.write('\n'.join(out))
        f.close()
    except:
        pass


def process_files(num_processes=4):
    files = os.listdir(CLEAN_EPUB_PATH)
    if num_processes == 1:
        for f in files:
            process(f)
    else:  # pragma: nocover
        pool = Pool(processes=num_processes)
        for _ in tqdm.tqdm(
            pool.imap_unordered(process, files),
            total=len(files)
        ):
            pass


def main():  # pragma: nocover
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=4
    )
    args = parser.parse_args()

    process_files(num_processes=args.num_processes)


if __name__ == '__main__':  # pragma: nocover
    main()
