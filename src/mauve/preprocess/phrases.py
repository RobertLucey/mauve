import spacy

from mauve.utils import get_en_core_web_sm


def replace_phrases(text: str) -> str:
    """
    Replace words with something more succinct or easier to process
    Sort of like a lemma for many words but very bad

    Custom words like "foreign affairs" for oirechtas which joins the
    words by an underscore since whatever is the actual way of doing
    this by category is too passive

    Usage:
        >>> replace_phrases('Is this in regard to something?')
        'Is this regarding something'
    """
    doc = get_en_core_web_sm(text)

    from mauve.preprocess.constants.phrases import PHRASE_MATCHER
    from mauve.preprocess.constants.replacements import REPLACEMENTS

    phrase_matches = PHRASE_MATCHER(doc)

    replacements = []

    for _, start, end in phrase_matches:
        span = doc[start:end]
        replacements.append(span)

    replacements = [f.text for f in spacy.util.filter_spans(replacements)]

    text = doc.text

    for name in replacements:
        text = text.replace(
            name,
            name.replace(' ', '_')
        )

    for name in REPLACEMENTS:
        if name in REPLACEMENTS:
            text = text.replace(
                name,
                REPLACEMENTS[name]
            )

    return text
