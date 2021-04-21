'''
This is gross. Should fix up heavily
'''
import argparse
import random
import json
import os
import re
from multiprocessing.pool import ThreadPool

from urllib.request import urlopen
import bs4

from mauve.constants import (
    GOODREADS_METADATA_PATH,
    TEXT_PATH
)
from mauve.utils import clean_filename


def get_id_from_isbn(data):
    try:
        title = data['title']
        source = urlopen('https://www.goodreads.com/search?&query=%s' % (data['isbn']))
        soup = bs4.BeautifulSoup(source, 'html.parser')

        book_id = None
        try:
            book_id = soup.find_all('input', {'id': 'book_id'})[0].get('value')
        except:
            pass

        if book_id is None:
            book_id = soup.find_all('div', {'class': 'u-anchorTarget'})[0]['id']

        return (
            title,
            data['original_filename'],
            book_id
        )
    except Exception as ex:
        pass
        # Could try as a backup, get from the title
        ##try:
        ##    return get_id_from_title(data)
        ##except Exception as ex:
        ##    print('EXCEPTION: ' + title + ' - ' + str(ex))
        ##    return None


def get_id_from_title(data):
    try:
        title = data['title']
        wrds = title.split(' ')  # + author.split(' ')
        source = urlopen('https://www.goodreads.com/search?&query=%s' % ('+'.join(wrds)))
        soup = bs4.BeautifulSoup(source, 'html.parser')
        return (
            title,
            data['original_filename'],
            soup.find_all('div', {'class': 'u-anchorTarget'})[0]['id']
        )
    except Exception as ex:
        print('EXCEPTION: ' + title + ' - ' + str(ex))
        return None


def get_genres(soup):
    genres = []
    for node in soup.find_all('div', {'class': 'left'}):
        current_genres = node.find_all(
            'a',
            {'class': 'actionLinkLite bookPageGenreLink'}
        )
        current_genre = ' > '.join([g.text for g in current_genres])
        if current_genre.strip():
            genres.append(current_genre.lower().strip())
    return genres


def get_isbn(soup):
    try:
        isbn = re.findall(
            r'nisbn: [0-9]{10}',
            str(soup)
        )[0].split()[1]
        return isbn
    except:
        return 'isbn not found'


def get_isbn13(soup):
    try:
        isbn13 = re.findall(
            r'nisbn13: [0-9]{13}',
            str(soup)
        )[0].split()[1]
        return isbn13
    except:
        return 'isbn13 not found'


def get_rating_distribution(soup):
    distribution = re.findall(
        r'renderRatingGraph\([\s]*\[[0-9,\s]+',
        str(soup)
    )[0]
    distribution = ' '.join(distribution.split())
    distribution = [
        int(c.strip()) for c in distribution.split('[')[1].split(',')
    ]
    distribution_dict = {
        '5 Stars': distribution[0],
        '4 Stars': distribution[1],
        '3 Stars': distribution[2],
        '2 Stars': distribution[3],
        '1 Star':  distribution[4]
    }
    return distribution_dict


def get_num_pages(soup):
    if soup.find('span', {'itemprop': 'numberOfPages'}):
        num_pages = soup.find(
            'span',
            {'itemprop': 'numberOfPages'}
        ).text.strip()
        return int(num_pages.split()[0])
    return ''


def get_year_first_published(soup):
    year_first_published = soup.find(
        'nobr',
        attrs={'class': 'greyText'}
    ).string
    return re.search('([0-9]{3,4})', year_first_published).group(1)


def get_id(bookid):
    pattern = re.compile('([^.-]+)')
    return pattern.search(bookid).group()

    
def scrape_book(book_id):
    url = 'https://www.goodreads.com/book/show/' + book_id
    source = urlopen(url)
    soup = bs4.BeautifulSoup(source, 'html.parser')

    try:
        return {
            'book_id': get_id(book_id),
            'book_title': ' '.join(
                soup.find('h1', {'id': 'bookTitle'}).text.split()
            ),
            'isbn': get_isbn(soup),
            'isbn13': get_isbn13(soup),
            'year_first_published': get_year_first_published(soup),
            'author': ' '.join(
                soup.find('span', {'itemprop': 'name'}).text.split()
            ),
            'num_pages': get_num_pages(soup),
            'genres': get_genres(soup),
            'num_ratings': soup.find(
                'meta',
                {'itemprop': 'ratingCount'}
            )['content'].strip(),
            'num_reviews': soup.find(
                'meta',
                {'itemprop': 'reviewCount'}
            )['content'].strip(),
            'average_rating': soup.find(
                'span',
                {'itemprop': 'ratingValue'}
            ).text.strip(),
            'rating_distribution': get_rating_distribution(soup)
        }
    except:
        pass


def get_title_id_cache():
    '''
    It's actually an id title map... should change that

    :return:
    :rtype: dict
    '''
    title_id_file = os.path.join(
        GOODREADS_METADATA_PATH,
        'title_id_map.json'
    )

    if os.path.exists(title_id_file):
        f = open(title_id_file, 'r')
        return json.loads(f.read())

    return {}


def get_request_chunk_items(files, title_id_cache):
    '''

    :param files:
    :param title_id_cache:
    '''
    titles = []
    count = 0
    for f in files:
        if '___' in f and '.json' not in f:
            title = f.split('___')[1].replace('.txt', '')
            isbn, author, title = f.split('___')
            title = title.replace('.txt', '')

            if f not in title_id_cache.values():
                if 'json' in title:
                    # this is a generated file so we shouldn't be processed
                    continue

                titles.append(
                    {
                        'title': title,
                        'original_filename': clean_filename(f),
                        'isbn': isbn
                    }
                )

                count += 1
                if count == 50:  # We brake here to batch in case connections drop. Write your own script around this if you like
                    break
    return titles


def write_title_id_cache(title_id_cache):
    '''

    :param title_id_cache: The new title_id_cache updated by the script
    '''
    title_id_file = os.path.join(
        GOODREADS_METADATA_PATH,
        'title_id_map.json'
    )
    f = open(title_id_file, 'w')
    f.write(json.dumps(title_id_cache))
    f.close()


def write_book_metadata(metadata_results):
    '''

    :param metadata_results:
    '''
    for scrape_result in metadata_results:
        if scrape_result is not None:
            json.dump(
                scrape_result,
                open(
                    os.path.join(
                        GOODREADS_METADATA_PATH,
                        scrape_result['book_id'] + '.json'
                    ),
                    'w'
                )
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--threads',
        type=int,
        default=20,
        dest='num_threads',
        help='num concurrent threads'
    )
    args = parser.parse_args()

    title_id_cache = get_title_id_cache()

    files = os.listdir(TEXT_PATH)
    random.shuffle(files)

    request_items = get_request_chunk_items(files, title_id_cache)

    print('Books to get: %s' % (len(request_items)))

    get_id_responses = []
    with ThreadPool(processes=args.num_threads) as pool:
        get_id_responses.extend(
            pool.map(
                get_id_from_isbn,
                request_items
            )
        )

    get_id_responses = [i for i in get_id_responses if i is not None]

    book_title_id_map = {}
    book_ids = []
    for _, original_filename, book_id in get_id_responses:
        book_title_id_map[book_id] = original_filename
        book_ids.append(book_id)

    title_id_cache.update(book_title_id_map)

    books_already_scraped = [
        file_name.replace('.json', '') for file_name in os.listdir(GOODREADS_METADATA_PATH) if file_name.endswith('.json')
    ]
    books_to_scrape = [
        book_id for book_id in book_ids if book_id not in books_already_scraped
    ]

    metadata_results = []
    with ThreadPool(processes=args.num_threads) as pool:
        metadata_results.extend(
            pool.map(
                scrape_book,
                books_to_scrape
            )
        )

    write_title_id_cache(title_id_cache)
    write_book_metadata(metadata_results)


if __name__ == '__main__':
    main()
