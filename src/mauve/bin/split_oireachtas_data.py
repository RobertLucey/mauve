import collections
import glob
import os
from multiprocessing import Pool

import tqdm

from tika import parser

from mauve.utils import get_file_content
from mauve.models.oireachtas.debate import (
    Debate,
    DebateSection,
    Speech,
    Para,
    merge_paras
)
from mauve.constants import ENG_WORDS
from mauve.models.text import Text


speakers = collections.defaultdict(list)

def process(fn):
    data = get_file_content(fn)

    for k, v in data.content_by_speaker.items():
        if any(48 <= ord(char) <= 57 for char in k):
            continue
        speakers[k].extend(v)

def main():
    files = []
    for filename in glob.iglob(
        os.path.join('/opt/mauve/oireachtas/', '**/*.pickle'),
        recursive=True
    ):
        files.append(filename)

    i = 0
    for f in files:
        i += 1
        process(f)

    speakers_count = collections.defaultdict(int)
    for k, v in speakers.items():
        speakers_count[k] += len(v)

    #merge_paras(speakers['#MickLanigan']).get_profanity_score()

    for k, v in speakers.items():
        score = merge_paras(speakers[k]).get_profanity_score()
        print(k)
        print(score)
        print()

    #import pdb; pdb.set_trace()
    #print()

    #pool = Pool(processes=4)
    #for _ in tqdm.tqdm(
    #    pool.imap_unordered(process, files),
    #    total=len(files)
    #):
    #    pass

if __name__ == '__main__':
    main()
