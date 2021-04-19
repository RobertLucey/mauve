import spacy
from spacy.matcher import Matcher

from mauve.constants import REPLACEMENTS
from mauve import ENCORE
from mauve.constants.idioms import IDIOMS, IDIOM_MATCHER


def replace_idioms(content: str) -> str:

    from mauve.constants import REPLACEMENTS

    sentence = ENCORE(content)

    phrase_matches = IDIOM_MATCHER(sentence)

    replacements = []

    for match_id, start, end in phrase_matches:
        span = sentence[start:end]
        replacements.append(span)

    replacements = [f.text for f in spacy.util.filter_spans(replacements)]

    content = sentence.text

    sub_replace = list(set([s.text for s in sentence.ents]))

    for name in replacements + sub_replace:

        content = content.replace(
            name,
            name.replace(' ', '_')
        )

    for name in REPLACEMENTS:
        if name in REPLACEMENTS:
            content = content.replace(
                name,
                REPLACEMENTS[name]
            )

    return content
