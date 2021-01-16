from ebooklib import epub


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
