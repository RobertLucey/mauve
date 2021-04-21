from mauve.preprocess.constants.spelling import AMERICAN_TO_ENGLISH_NORMALIZER


def normalize_spelling(content: str) -> str:
    for k, replacement in AMERICAN_TO_ENGLISH_NORMALIZER.items():
        if k in content:
            content = content.replace(k, replacement)

    return content
