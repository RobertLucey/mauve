import re


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
