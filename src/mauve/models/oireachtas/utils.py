import datetime
import os
import random
from collections import defaultdict

from mauve.constants import RAW_OIREACHTAS_DIR
from mauve.models.text import TextBody
from mauve.models.oireachtas.debate import Debate, Para


def merge_paras(paras):
    '''
    When you don't care about context it's often easier to treat many
    paragraphs as one.

    :param paras:
    :return: A Para object that just merges all the paras you give it into one.
    '''
    return Para(content='\n\n'.join([m.content for m in paras]))


def iter_debates(
    max_debates=None,
    start_date=datetime.datetime.min,
    end_date=datetime.datetime.max
):
    filenames = os.listdir(RAW_OIREACHTAS_DIR)
    random.shuffle(filenames)

    for idx, fp in enumerate(filenames):
        debate = Debate(
            file_path=os.path.join(RAW_OIREACHTAS_DIR, fp)
        )
        if debate.date < start_date or debate.date > end_date:
            break
        if max_debates is not None and idx == max_debates:
            break
        yield debate


def get_text_by_speaker(
    max_debates=None,
    start_date=datetime.datetime.min,
    end_date=datetime.datetime.max
):
    speaker_para_map = defaultdict(list)
    for idx, debate in enumerate(
        iter_debates(
            max_debates=max_debates,
            start_date=start_date,
            end_date=end_date
        )
    ):
        for speaker, paras in debate.content_by_speaker.items():
            speaker_para_map[speaker].extend(paras)

    speaker_text_map = defaultdict(TextBody)
    for speaker, paras in speaker_para_map.items():
        speaker_text_map[speaker] = merge_paras(paras)

    return speaker_para_map
