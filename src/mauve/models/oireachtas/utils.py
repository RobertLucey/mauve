import os
import random
from collections import defaultdict

from mauve.constants import RAW_OIREACHTAS_DIR
from mauve.models.oireachtas.debate import Debate


def iter_debates():

    filenames = os.listdir(RAW_OIREACHTAS_DIR)
    random.shuffle(filenames)

    for fp in filenames:
        yield Debate(file_path=os.path.join(RAW_OIREACHTAS_DIR, fp))


def get_text_by_speaker():
    speaker_para_map = defaultdict(list)
    for debate in iter_debates():
        for speaker, paras in debate.content_by_speaker.items():
            speaker_para_map[speaker].extend(paras)
    return speaker_para_map
