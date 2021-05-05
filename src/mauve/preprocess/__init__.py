import logging

from mauve.preprocess.number_convert import convert_numbers
from mauve.preprocess.spelling import normalize_spelling
from mauve.preprocess.contractions import (
    replace_contractions,
)
from mauve.preprocess.utils import (
    replace_ellipsis,
    remove_decimal_separators,
    guess_speech_quote
)
from mauve.settings import (
    PREPROCESS_NORMALIZE_SPELLING,
    PREPROCESS_NUMBER_CONVERT
)

logger = logging.getLogger('mauve')


def clean(content: str, lang='en') -> str:
    """
    Try to take weird and cumbersome stuff out of the text.
    Mainly around contractions and quoting to make things less ambiguous
    """
    content = replace_contractions(content)
    content = replace_ellipsis(content)
    content = remove_decimal_separators(content)

    if PREPROCESS_NUMBER_CONVERT:
        content = convert_numbers(content)

    if lang == 'en' and PREPROCESS_NORMALIZE_SPELLING:
        content = normalize_spelling(content)

    guessed_quote = guess_speech_quote(content)
    if guessed_quote == '’':
        # Just to be safe don't change all the single quotes, just change
        # the ones that are posessive (FIXME: deal with the others)
        logger.debug('Speech quote guessed is %s so only changing posessives ’s', guessed_quote)
        content = content.replace('’s', '\'s')
    else:
        logger.debug('Speech quote guessed is %s so dangerously modifying ’ to \'', guessed_quote)
        content = content.replace('’', '\'')
    return content
