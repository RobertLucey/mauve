import os
import random
from collections import defaultdict

from mauve.constants import RAW_OIREACHTAS_DIR
from mauve.models.oireachtas.debate import Debate, Para


def merge_paras(paras):
    '''
    When you don't care about context it's often easier to treat many
    paragraphs as one.

    :param paras:
    :return: A Para object that just merges all the paras you give it into one.
    '''
    return Para(content='\n\n'.join([m.content for m in paras]))


def iter_debates():
    filenames = os.listdir(RAW_OIREACHTAS_DIR)
    random.shuffle(filenames)

    for fp in filenames:
        yield Debate(file_path=os.path.join(RAW_OIREACHTAS_DIR, fp))


def get_text_by_speaker():
    speaker_para_map = defaultdict(list)
    for idx, debate in enumerate(iter_debates()):
        for speaker, paras in debate.content_by_speaker.items():
            speaker_para_map[speaker].extend(paras)

    speaker_text_map = {}
    for speaker, paras in speaker_para_map.items():
        speaker_text_map[speaker] = merge_paras(paras)

    return speaker_para_map
