import argparse
import random
import os
import time
from urllib.request import urlopen
from urllib.request import urlretrieve
from multiprocessing.pool import ThreadPool
from urllib.parse import unquote

import tqdm
import bs4

from mauve.constants import EPUB_PATH
from mauve.utils import clean_filename


def download(data):
    category = data[0]
    filename = data[1]

    if not '.epub' in filename:
        return

    if '..' in filename:
        return

    dl_url = 'https://the-eye.eu/public/Books/Bibliotik/{}/{}'.format(category, filename)

    try:
        filename = os.path.join(EPUB_PATH, clean_filename(unquote(filename)))
        urlretrieve(dl_url, filename)
        time.sleep(0.5)
    except Exception as ex:
        try:
            os.remove(filename)
        except:
            pass


def parse_size(number, unit):
    units = {'K': 10 ** 3, 'M': 10 ** 6, 'G': 10 ** 9}
    return int(float(number) * units[unit])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--category',
        type=str,
        default='A',
        help='single char 0-9A-Z'
    )
    parser.add_argument(
        '--shuffle',
        action='store_true',
        dest='shuffle',
        help='to shuffle the items to download'
    )
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=2
    )
    parser.add_argument(
        '--max-bytes',
        type=int,
        dest='max_bytes',
        default=10000000  # 10M
    )

    args = parser.parse_args()

    base_url = 'https://the-eye.eu/public/Books/Bibliotik/'

    source = urlopen(base_url + '%s/' % (args.category.upper()))
    soup = bs4.BeautifulSoup(source, 'html.parser')
    pre = soup.find_all('pre')[0]

    count = 0
    fns = []
    cache = []
    for p in pre:
        try:
            if count % 2 == 1:
                count += 1
                number = str(p).strip().split(' ')[-1][0:-1]
                unit = str(p).strip().split(' ')[-1][-1]
                try:
                    size = parse_size(number, unit)
                except ValueError:
                    print('Can\'t get size from: %s' % (p))
                else:
                    if size < args.max_bytes:
                        fns.extend(cache)
                    cache = []

            fn = p.get('href')
            if os.path.exists(os.path.join(EPUB_PATH, unquote(fn))):
                continue
            count += 1
            cache.append((args.category.upper(), fn))
        except AttributeError:
            pass

    print('REMAINING: %s' % (len(fns)))

    if args.shuffle:
        random.shuffle(fns)

    pool = ThreadPool(processes=args.num_processes)
    for _ in tqdm.tqdm(
            pool.imap_unordered(download, fns),
            total=len(fns)
    ):
        pass


if __name__ == '__main__':
    main()
