import logging

from word2number import w2n

logger = logging.getLogger('mauve')

# check words in w2n.american_number_system

maximum = 999999999


words = []
for w in w2n.american_number_system.keys():
    words.append(' ' + w)
    words.append('-' + w)
    words.append(w)
    words.append(w.capitalize())


def index(content: str, substr: str, idx: int) -> int:
    try:
        return content.index(substr, idx)
    except ValueError:
        return maximum


def _find_next_instance(content: str, idx=0) -> tuple:
    indexes = [(s, index(content, s, idx)) for s in words]
    min_index = min([i[1] for i in indexes])
    return (
        min_index,
        [i[0] for i in indexes if i[1] == min_index][0]
    )


def get_word_at(content: str, index: int) -> int:
    return content[get_word_start_index(content, index):].strip().replace('-', ' ')


def get_word_start_index(content: str, index: int) -> int:
    return max([content.rfind(' ', 0, index + 1), 0])


def get_next(content: str, idx=0):
    idx = min([index(content, ' ', idx=idx), index(content, '-', idx=idx)])
    if idx == maximum:
        if content is None:
            return None, None
        return content.strip(), None
    return content[:idx].strip(), content[idx:].strip()


def _is_wordy(word):
    if word is None:
        return False
    if word.strip() in words:
        return True
    if word.strip() in {'and', 'a'}:
        return True
    if word.split('-')[0] in words:
        return True
    return False


def contains_number(content: str) -> bool:
    for num_word in w2n.american_number_system.keys():
        if num_word in content:
            return True
    return False


def convert_numbers(content: str) -> str:

    def _replace(content: str) -> str:
        first_index, first_word = _find_next_instance(content, idx=0)
        if first_index == maximum:
            # No numberey bits
            return content

        before_content = content[:get_word_start_index(content, first_index)]
        after_excluding = content[first_index + len(first_word):]

        next_content = after_excluding
        running = [first_word.strip()]
        to_extend = ''

        while True:
            next_word, next_content = get_next(next_content, idx=1)
            if _is_wordy(next_word):
                running.append(next_word.strip())
            else:
                if next_word is not None and next_content is not None:
                    to_extend = next_word + ' ' + next_content
                elif next_word is not None and next_content is None:
                    to_extend = next_word
                else:
                    to_extend = ''
                break

        return before_content + ' ' + str(w2n.word_to_num(' '.join(running))) + ' ' + to_extend

    matching = False
    while not matching:
        if contains_number(content):
            tmp_content = _replace(content)
            matching = tmp_content == content
            content = tmp_content
        else:
            break

    return str(content).strip()
