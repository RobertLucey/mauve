import argparse
import random
import json
import os
import requests
import re
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

import tqdm

from urllib.request import Request
from urllib.request import urlopen
from urllib.request import HTTPError

import bs4
import time

from mauve.models.oireachtas.debate import Debate
from mauve.constants import TEXT_PATH


def scrape_debates(d):
    d.load_data()
    d.write()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=20
    )
    args = parser.parse_args()


    chamber_type = 'house'  # committee
    chamber_id = ''
    chamber = ''
    date_start = '1900-01-01'
    date_end = '1990-06-01'
    limit = '1000'

    req = Request(
        'https://api.oireachtas.ie/v1/debates?chamber_type=%s&chamber_id=%s&chamber=%s&date_start=%s&date_end=%s&limit=%s' % (
            chamber_type,
            chamber_id,
            chamber,
            date_start,
            date_end,
            limit
        ),
        headers={'accept': 'application/json'}
    )
    response = urlopen(req)
    data = json.loads(response.read())

    debates = []
    for d in data['results']:
        debates.append(
            Debate(
                date=d['contextDate'],
                chamber=d['debateRecord']['chamber']['showAs'],
                counts=d['debateRecord']['counts'],
                debate_type=d['debateRecord']['debateType'],
                debate_sections=d['debateRecord']['debateSections']
            )
        )

    pool = ThreadPool(processes=args.num_processes)
    for _ in tqdm.tqdm(
        pool.imap_unordered(scrape_debates, debates),
        total=len(debates)
    ):
        pass

if __name__ == '__main__':
    main()
