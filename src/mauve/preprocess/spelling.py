from mauve.preprocess.constants.spelling import AMERICAN_TO_ENGLISH_NORMALIZER

from flashtext import KeywordProcessor
keyword_processor = KeywordProcessor()

for f, t in AMERICAN_TO_ENGLISH_NORMALIZER.items():
    keyword_processor.add_keyword(f, t)


def normalize_spelling(content: str) -> str:
    return keyword_processor.replace_keywords(content)
