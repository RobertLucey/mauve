import argparse
import os
import json
from multiprocessing.pool import ThreadPool
from urllib.request import (
    urlopen,
    Request
)

import tqdm

from mauve.constants import RAW_OIREACHTAS_DIR


def scrape_debates(d):

    date = d['contextDate']
    chamber = d['debateRecord']['chamber']['showAs'].split()[0].lower()

    filename = '{}_{}.json'.format(date, chamber)

    if os.path.exists(os.path.join(RAW_OIREACHTAS_DIR, filename)):
        return

    for section in d['debateRecord']['debateSections']:

        section_uri = section['debateSection']['formats']['xml']['uri']

        try:
            section['debateSection']['data'] = urlopen(
                section_uri
            ).read().decode('utf-8')
        except Exception:
            section['debateSection']['data'] = None

    with open(os.path.join(RAW_OIREACHTAS_DIR, filename), 'w') as outfile:
        json.dump(d, outfile)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=50
    )
    args = parser.parse_args()

    chamber_type = 'house'  # committee
    chamber_id = ''
    chamber = ''
    date_start = '1900-01-01'
    date_end = '2021-01-01'
    limit = '1000'

    url = 'https://api.oireachtas.ie/v1/debates?chamber_type=%s&chamber_id=%s&chamber=%s&date_start=%s&date_end=%s&limit=%s' % (
        chamber_type,
        chamber_id,
        chamber,
        date_start,
        date_end,
        limit
    )

    req = Request(
        url,
        headers={'accept': 'application/json'}
    )
    response = urlopen(req)
    data = json.loads(response.read())

    pool = ThreadPool(processes=args.num_processes)
    for _ in tqdm.tqdm(
        pool.imap_unordered(scrape_debates, data['results']),
        total=len(data['results'])
    ):
        pass


if __name__ == '__main__':
    main()
