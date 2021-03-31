"""
Badly optimized, fight me
"""

import glob
import argparse
import os
from multiprocessing import Pool

import tqdm

from mauve.constants import BASE_DATA_PATH
from mauve.utils import compress_file


def _compress_file(fp):
    if os.path.exists(fp + '.bz'):
        os.remove(fp)
    else:
        compress_file(fp)
        os.remove(fp)


def compress(num_processes=4):
    files = []
    for filename in glob.iglob(
            os.path.join(BASE_DATA_PATH, '**/*.pickle'),
            recursive=True
    ):
        files.append((filename, os.path.getsize(filename)))

    files = [
        b[0] for b in sorted(
            files,
            key=lambda tup: tup[1],
            reverse=True
        )
    ]

    if num_processes == 1:
        for f in files:
            _compress_file(f)
    else:  # pragma: nocover
        pool = Pool(processes=num_processes)
        for _ in tqdm.tqdm(
                pool.imap_unordered(_compress_file, files),
                total=len(files)
        ):
            pass


def main():  # pragma: nocover

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        dest='num_processes',
        default=1
    )
    args = parser.parse_args()

    compress(num_processes=args.num_processes)


if __name__ == '__main__':  # pragma: nocover
    main()
