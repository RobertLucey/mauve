# TODO: handle fractional words "half a million" "a quarter of a billion"
# TODO: Only if after the word negative or minus is numberey should it be replaced with -

import sys
import logging

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

words = []
for w in w2n.american_number_system.keys():
    words.append(' ' + w)
    words.append('-' + w)
    words.append(w)
    words.append(w.capitalize())


def index(content: str, substr: str, idx: int) -> int:
    try:
        return content.index(substr, idx)
    except (ValueError, AttributeError):
        return sys.maxsize


def _find_next_instance(content: str, idx=0) -> tuple:
    """
    Find the next instance of a numberey word
    """
    indexes = [(s, index(content, s, idx)) for s in words]
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
    return content[:idx].strip(), content[idx:].strip()


def _is_numberey(word: str) -> bool:
    """
    Is the given word likely contained in a number expression
    """
    if word is None:
        return False
    word = word.replace(',', '').replace('!', '').replace('.', '').replace('?', '')
    if word.strip() in words:
        return True
    if word.strip() in {'and', 'a'}:
        return True
    if word.split('-')[0] in words:
        return True
    return False


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
    return [n.replace(',', '').replace('!', '').replace('.', '').replace('?', '').strip() for n in number_list]


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
    cleaned = clean_for_word_to_num(number_words)
    parsed_unordered = parse_unordered(number_words)
    if parsed_unordered is not None:
        return str(parsed_unordered)

    return str(w2n.word_to_num(' '.join(cleaned)))


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
        first_index, first_word = _find_next_instance(content, idx=0)
        if first_index == sys.maxsize:
            # No numberey bits
            return content

        idx = 1
        if content[first_index-idx].isdigit():
            while True:
                idx += 1
                if any([
                    first_index - idx < 0,
                    not content[first_index - idx].isdigit()
                ]):
                    break
            pre = content[0: first_index - idx + 1]
            post = content[first_index + len(first_word):]
            return pre + str(int(content[first_index - idx + 1: first_index]) * w2n.word_to_num(first_word)) + post

        before_content = content[:get_word_start_index(content, first_index)]
        after_excluding = content[first_index + len(first_word):]
        next_content = after_excluding
        number_words = [first_word.strip()]
        to_extend = ''

        while True:
            next_word, next_content = get_next(next_content, idx=1)
            if _is_numberey(next_word):
                number_words.append(next_word.strip())
            else:
                if next_word is not None and next_content is not None:
                    to_extend = next_word + ' ' + next_content
                elif next_word is not None and next_content is None:
                    to_extend = next_word
                else:
                    to_extend = ''
                break

        if number_words[0] in {'hundred', 'thousand', 'million', 'billion', 'trillion'}:
            number_words.insert(0, 'one')

        return before_content + ' ' + word_to_num(number_words) + ' ' + to_extend

    matching = False
    while not matching:
        if contains_wordy_number(content):
            tmp_content = _replace(content)
            matching = tmp_content == content
            content = tmp_content
        else:
            break

    return str(content).strip()
