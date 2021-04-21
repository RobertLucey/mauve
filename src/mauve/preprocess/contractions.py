from mauve.preprocess.constants.contractions import CONTRACTION_MAP
from mauve.constants import APOSTROPHES


def replace_contractions(content: str) -> str:
    """
    Expand contractions since contractions are annoying

    Doesn't work all the time cause he's can mean 'he is'
    or 'he was'

    Usage:
        >>> replace_contractions('y\'all willn\'t smack ol\' maw')
        'you all will not smack old maw'
    """
    for appos in APOSTROPHES:
        if appos not in content:
            continue
        for k, replacement in CONTRACTION_MAP.items():
            find = k.replace('\'', appos)
            if find in content:
                content = content.replace(find, replacement)

    return content
