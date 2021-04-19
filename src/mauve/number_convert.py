import logging

from word2number import w2n

logger = logging.getLogger('mauve')

# check words in w2n.american_number_system


def contains_number(content: str) -> bool:
    for num_word in w2n.american_number_system.keys():
        if num_word in content:
            return True
    return False


def convert_numbers(content: str) -> str:
    # Maybe split by newlines to deal with smaller pieces
    # can't split by . or ,

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
        except:
            return maximum

    def _find_next_instance(content: str, idx=0) -> tuple:
        indexes = [(s, index(content, s, idx)) for s in words]
        min_index = min([i[1] for i in indexes])
        return (
            min_index,
            [i[0] for i in indexes if i[1] == min_index][0]
        )

    def get_word_at(content: str, index: int) -> int:
        return content[get_word_start_index(content, index):].strip().split(' ')[0]

    def get_word_start_index(content: str, index: int) -> int:
        return max([content.rfind(' ', 0, index + 1), 0])

    def _replace(content: str) -> str:
        next_index, next_word = _find_next_instance(content, idx=0)
        if next_index == maximum:
            return content

        before_content = content[:get_word_start_index(content, next_index)]
        after_including = content[get_word_start_index(content, next_index):]
        after_excluding = content[next_index + len(next_word):]

        # If it's the last word
        if after_including in words:
            return before_content + ' ' + str(w2n.word_to_num(get_word_at(content, next_index))) + after_excluding

        # If it's not the last word but all words after are numberey
        if all(
            [w in words for w in after_including.replace('-', ' ').split(' ')]
        ):
            return before_content + ' ' + str(w2n.word_to_num(after_including))

        # If there are no more numberey words after the first can just change the one word
        next_index, _ = _find_next_instance(after_excluding, idx=0)
        if next_index == maximum:
            return before_content + ' ' + str(w2n.word_to_num(next_word)) + ' ' + after_excluding

        # TODO: less trivial

        return content

    matching = False
    while not matching:
        if contains_number(content):
            tmp_content = _replace(content)
            matching = tmp_content == content
            content = tmp_content
        else:
            break
    return str(content)
