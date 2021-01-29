# Do not use this, it will mess your data up


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
    Para
)
from mauve.constants import ENG_WORDS


def join_splits(lines):
    tot = []
    join_next = False
    tally = ''
    for l in lines:
        if join_next:
            tally += l
            join_next = False
            tot.append(tally)
            tally = ''
            continue
    
        if l[-1] == '-':
            join_next = True
            tally = l[0:-1]
            continue
    
        tot.append(l)

    return tot


def clean(lines):

    final_lines = []
    for l in lines:

        eng = [
            w for w in l.split(' ') if w.lower() in ENG_WORDS
        ]

        if float(len(eng)) / len(l.split(' ')) < 0.2:
            continue
        final_lines.append(l.replace('�', ''))
    return final_lines


def sections_to_speeches(sections):
    speeches = []
    for s in sections.values():
        by = s[0].split(':')[0].split('0')[-1]
        s[0] = ' '.join(s[0].split(':')[1:])
        content = ' '.join(s)

        paras = [Para(content=content)]

        speeches.append(
            Speech(
                by=by,
                paras=paras
            )
        )
    return speeches


def lines_to_sections(lines, date):
    sections = collections.defaultdict(list)
    idx = 0
    for f in lines:
        if f.startswith(date):
            idx += 1

        sections[idx].append(f)
    return sections


def process(fn):
    y, m, d = fn.split('_')[-1].replace('.pdf', '').split('-')
    date = '/'.join([d, m, y])
    raw = parser.from_file(fn)
    try:
        lines = raw['content'].split('\n')
    except:
        print('Bad file: %s' % (fn))
        return

    final = join_splits(join_splits(clean(lines)))

    sections = lines_to_sections(final, date)
    speeches = sections_to_speeches(sections)

    mock_section = DebateSection(
        bill=None,
        contains_debate=None,
        counts=None,
        debate_section_id=None,
        debate_type=None,
        data_uri=None,
        parent_debate_section=None,
        show_as=None,
        speakers=None,
        speeches=speeches
    )

    pickle_location = fn.replace('pdf', 'pickle')
    data = get_file_content(pickle_location)

    data.debate_sections.append(mock_section)

    data.write()
    os.remove(fn)


def main():
    return # because danger danger you see?
    files = []
    for filename in glob.iglob(
        os.path.join('/opt/mauve/oireachtas/', '**/*.pdf'),
        recursive=True
    ):
        files.append(filename)

    pool = Pool(processes=4)
    for _ in tqdm.tqdm(
        pool.imap_unordered(process, files),
        total=len(files)
    ):
        pass


if __name__ == '__main__':
    main()
