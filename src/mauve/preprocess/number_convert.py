# TODO: handle fractional words "half a million" "a quarter of a billion"
# TODO: Only if after the word negative or minus is numberey should it be replaced with -
# TODO: Roman numerals?

# Second can be like hour, minute, second so that'll be a toughie. Maybe one second would go to 12, sort of like "the first twenty years" thing below

# FIXME: fifteen-year-old => 15 year-old
# FIXME: two and two is four => 2 and 2 is 4
#    complicated since and is numberey

import copy
import sys
import logging

from mauve.constants import EXTENDED_PUNCTUATION
from mauve.preprocess import w2n

logger = logging.getLogger('mauve')

# TODO: handle minus words
#       After converting to numbers check this for handiness sake
negative_signifiers = {
    'minus',
    'negative'
}

ordinals = {
    'first': 1,
    'second': 2,
    'third': 3,
    'fourth': 4,
    'fifth': 5,
    'sixth': 6,
    'seventh': 7,
    'eighth': 8,
    'ninth': 9,
    'tenth': 10,
    'eleventh': 11,
    'twelfth': 12,
    'thirteenth': 13,
    'fourteenth': 14,
    'fifteenth': 15,
    'sixteenth': 16,
    'seventeenth': 17,
    'eighteenth': 18,
    'nineteenth': 19
}

extra = {
    #'grand': 1000,  # Want to use this but can be used in other contexts. If word / number before is numberey we can use it
    #'dozen': 12,  # five dozen should be 60, not 512
    'nil': 0,
    'nought': 0,
    'naught': 0,
}
w2n.american_number_system.update(ordinals)
w2n.american_number_system.update(extra)


IGNORABLE_PUNCT = copy.copy(EXTENDED_PUNCTUATION)
IGNORABLE_PUNCT.remove('-')


def remove_boring_chars(content: str):
    for boring in IGNORABLE_PUNCT:
        content = content.replace(boring, '')
    return content


def index(content: str, substr: str, idx: int) -> int:
    try:
        return content.index(substr, idx)
    except (ValueError, AttributeError):
        return sys.maxsize


def _find_next_instance(content: str, idx=0) -> tuple:
    """
    Find the next instance of a numberey word
    """
    indexes = [(s, index(content, s, idx)) for s in w2n.american_number_system.keys()]
    min_index = min([i[1] for i in indexes])
    max_len_at_index = max([len(i[0]) for i in indexes if i[1] == min_index])
    return (
        min_index,
        [i[0] for i in indexes if i[1] == min_index and len(i[0]) == max_len_at_index][0]
    )


def get_word_at(content: str, index: int) -> int:
    """
    Get the word at the position of the index
    """
    return content[get_word_start_index(content, index):].strip().replace('-', ' ')


def get_individual_word_at(content: str, index: int) -> int:
    """
    Get the word at the position of the index
    """
    return content[get_word_start_index(content, index):].strip().split()[0]


def get_word_start_index(content: str, index: int) -> int:
    """
    Get the start of the word at the position of the index
    """
    return max([content.rfind(' ', 0, index + 1), 0])


def get_next(content: str, idx=0):
    """
    Get the next word / wordy thing from an index. A stupid enough
    way of stepping through a string's content
    """
    idx = min([index(content, ' ', idx=idx), index(content, '-', idx=idx)])
    if idx == sys.maxsize:
        if content is None:
            return None, None
        return content.strip(), None
    return content[:idx], content[idx:]


def _is_numberey(word: str) -> bool:
    """
    Is the given word likely contained in a number expression
    """
    is_numberey = False
    if word is None:
        is_numberey = False
    try:
        word = remove_boring_chars(word)
    except:
        is_numberey = False
    else:
        cleaned = word.strip().lower()
        if cleaned == '':
            is_numberey = False
        elif cleaned[0] == '-':
            cleaned = cleaned[1:]

        if cleaned in w2n.american_number_system.keys():
            is_numberey = True
        elif cleaned in {'and', 'a'}:
            is_numberey = True
        elif word.split('-')[0] in w2n.american_number_system.keys():
            is_numberey = True
    return is_numberey


def contains_wordy_number(content: str) -> bool:
    """
    Does the string contain wordy numbers.

    Gives some false positives: "dog ate a bone" would find one but
    fail on getting the full word
    """
    for num_word in w2n.american_number_system.keys():
        if num_word in content:
            return True
    return False


def clean_for_word_to_num(number_list: list) -> list:
    """
    Clean a number word list for processing
    """
    def cut_ends(lst):
        if lst[-1] in {'a', 'and'}:
            return cut_ends(lst[:-1])
        if not isinstance(lst, list):
            return [lst]
        return lst

    if not isinstance(number_list, list):
        return number_list
    temp_clean = [remove_boring_chars(n).strip() for n in number_list]
    temp_clean = cut_ends(temp_clean)
    return temp_clean


def parse_unordered(number_words: list) -> int:
    """
    handle weird number lists like for dates [nineteen, eighty, one](1981)
    or colloquial numbers like [one, fifty](150) that word2number isn't
    great at
    """

    if len(number_words) == 3:
        first_number = w2n.word_to_num(number_words[0])
        second_number = w2n.word_to_num(number_words[1])
        third_number = w2n.word_to_num(number_words[2])

        if all([
            first_number > 0,
            first_number < 21,
            second_number < 100,
            second_number % 10 == 0,
            third_number < 10,
        ]):
            return int(str(first_number) + str(second_number + third_number))

    elif len(number_words) == 2:
        first_number = w2n.word_to_num(number_words[0])
        second_number = w2n.word_to_num(number_words[1])

        if all([
            first_number > 0,
            first_number < 21,
            second_number < 100,
            second_number % 10 == 0 or second_number < 20,
            second_number >= first_number
        ]):
            return int(str(first_number) + str(second_number))

    return None


def word_to_num(number_words: list) -> str:
    """
    Given a list of numberey words, give back the string integer representation

    Usage:
        >>> word_to_num(['fifty', 'three'])
        '53'
    """
    try:
        cleaned = clean_for_word_to_num(number_words)
        if cleaned == ['point']:
            raise ValueError('Not a number')
        if len(cleaned) > 1 and cleaned[0].lower() in ordinals.keys():
            # This is a bit icky
            return number_words[0] + ' ' + word_to_num(number_words[1:])
        parsed_unordered = parse_unordered(cleaned)
        if parsed_unordered is not None:
            logger.debug('word_to_num: %s -> %s', number_words, parsed_unordered)
            return str(parsed_unordered)
        logger.debug('word_to_num: %s -> %s', number_words, w2n.word_to_num(' '.join(cleaned)))
        return str(w2n.word_to_num(' '.join(cleaned)))
    except ValueError as ex:
        logger.warning('Could not word_to_num: %s', number_words)
        logger.warning(ex)
        return ' '.join(number_words)


def convert_numbers(content: str) -> str:
    """
    Given a string, convert where possible words to numbers

    Usage:
        >>> convert_numbers('about 600 million or so')
        'about 600000000 or so'

        >>> convert_numbers('zero Something fifty three blah blah one')
        '0 Something 53 blah blah 1'
    """
    def _replace(content: str) -> str:
        first_index, first_word = _find_next_instance(content.lower(), idx=0)
        if first_index == sys.maxsize:
            # No numberey bits
            return content

        captured_word = get_individual_word_at(content, first_index)

        idx = 1
        if content[first_index - (idx + 1)].isdigit():
            while True:
                idx += 1
                if any([
                    first_index - idx < 0,
                    not content[first_index - idx].isdigit()
                ]):
                    break
            pre = content[0: first_index - idx + 1]
            post = content[first_index + len(first_word):]
            return pre + str(int(content[first_index - idx + 1: first_index]) * w2n.word_to_num(first_word)) + _replace(post)

        before_content = content[:get_word_start_index(content, first_index)]
        after_excluding = content[first_index + len(first_word):]
        next_content = after_excluding
        number_words = [first_word.strip()]
        to_extend = ''

        if not _is_numberey(captured_word):
            try:
                n = content.index(' ', first_index + len(first_word))
            except Exception:
                n = len(content)
            after_excluding_wordy = content[n + 1:]
            return before_content + ' ' + captured_word + ' ' + _replace(after_excluding_wordy).strip(' -')

        while True:
            pre = next_content
            next_word, next_content = get_next(next_content, idx=1)
            if _is_numberey(next_word):
                number_words.append(next_word.strip())
            else:
                if next_word is not None and next_content is not None:
                    to_extend = pre
                elif next_word is not None and next_content is None:
                    to_extend = next_word
                else:
                    to_extend = ''
                break

        if number_words[0] in {'hundred', 'thousand', 'million', 'billion', 'trillion'}:
            number_words.insert(0, 'one')

        return before_content + ' ' + word_to_num(number_words) + ' ' + _replace(to_extend).strip(' -')

    converted_lines = []
    newlines = content.split('\n')
    for newline in newlines:
        converted_lines.append(
            '. '.join(_replace(sentence).strip() for sentence in newline.split('. '))
        )
    return '\n'.join(converted_lines)
