import os
import random

from mauve.constants import RAW_OIREACHTAS_DIR
from mauve.models.oireachtas.debate import Debate


def iter_debates():

    filenames = os.listdir(RAW_OIREACHTAS_DIR)
    random.shuffle(filenames)

    for fp in filenames:
        yield Debate(file_path=os.path.join(RAW_OIREACHTAS_DIR, fp))
