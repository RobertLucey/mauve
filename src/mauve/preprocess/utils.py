import re
import logging
from collections import Counter

from mauve.constants import (
    SPEECH_QUOTES,
    SPEECH_WORDS
)

logger = logging.getLogger('mauve')


def replace_ellipsis(content: str) -> str:
    for to_replace in {'....', '. . . .', '...', '. . .'}:
        content = content.replace(to_replace, '…')
    return content


def remove_decimal_separators(content: str) -> str:
    return re.sub(r'(\d)\,(\d)', r'\1\2', content)


def clean_gutenberg(content: str) -> str:
    """
    Project Gutenberg texts come with headers and footers that
    have legal stuff in them and some other bits we don't want.
    This should clean up most of the rubbish.

    :param content: str content
    :return: The string content with Gutenberg boilerplace removed
    """

    if 'PROJECT GUTENBERG EBOOK' not in content:
        return content

    lines = content.split('\n')
    start, end = sorted(
        [
            idx for idx, line in enumerate(lines) if all([
                '***' in line,
                any([
                    'START OF THE PROJECT GUTENBERG EBOOK' in line,
                    'END OF THE PROJECT GUTENBERG EBOOK' in line
                ])
            ])
        ]
    )
    content = '\n'.join(lines[start + 1:end])

    content = content.replace('\n\n', 'MAUVE_REPLACE_NEWLINE')
    content = content.replace('\n', ' ').replace('MAUVE_REPLACE_NEWLINE', '\n')

    return content


def guess_speech_quote(content: str, default='"') -> str:
    """
    Given a piece of text guess what type of quote is used for speech

    :param content:
    :kwarg default: what to give back if couldn't make a good guess
    """
    speech_words = []
    for line in content.split('\n'):
        if any([word in line for word in SPEECH_WORDS]):
            speech_words.extend(
                [
                    l for l in list(line) if l in SPEECH_QUOTES
                ]
            )
    try:
        return list(Counter(speech_words).items())[0][0]
    except Exception:
        # Likely is no speech but give back something to be nice
        logger.debug('Could not guess speech quotes, assuming \'%s\'', default)
        return default
