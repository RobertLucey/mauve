import spacy
from spacy.matcher import Matcher
from mauve.structure.conditional import CONDITIONAL_LIST
from mauve.utils import get_en_core_web_sm
from mauve import ENCORE_LG


M_TOOL = Matcher(ENCORE_LG.vocab)


OTHER_REPLACEMENTS = {
    'mr.': 'mr',
    'mrs.': 'mrs',
    'dr.': 'dr',
    'ms.': 'ms',
    'Mr.': 'Mr',
    'Mrs.': 'Mrs',
    'Dr.': 'Dr',
    'Ms.': 'Ms',
    'in favour': 'in_favour',
    'general election': 'general_election',
    'reap the benefit': 'benefit',
    'much longer': 'much_longer',
    'a great help': 'helpful',
    'absolutely necessary': 'necessary',
    'in regard to': 'regarding',
    'in regards to': 'regarding',
    'i\'m': 'i am',
    'a bit difficult': 'difficult',
    'per annum': 'yearly',
    'a good thing': 'good',
    'sinn féin': 'sinn_fein',
    'don\'t': 'do not',
    'it\'s': 'it is',
    'a great deal': 'a lot',
    'fully aware': 'aware',
    'motor car': 'car'
}  # TODO: test this


GOV_BODIES = [
    'agriculture, food and the marine',
    'children, equality, disability, integration and youth',
    'defence',
    'education',
    'enterprise, trade and employment',
    'finance',
    'foreign affairs',
    'further and higher education, research, innovation and science',
    'health',
    'housing, local government and heritage',
    'local government',  # still bad?
    'justice',
    'public expenditure and reform',
    'rural and community development',
    'social protection',
    'the environment, climate and communications',
    'the taoiseach',
    'tourism, culture, arts, gaeltacht, sport and media',
    'transport',
    'agriculture',
    'enterprise, trade and employment',
    'tourism, sport and recreation',
    'industry and commerce',
    'the environment'
]

JOINERS = {
    'department of {}': GOV_BODIES,
    'minister for {}': GOV_BODIES,
    'minister of {}': GOV_BODIES,
}

CONDITIONALS = {c: c.replace(' ', '_') for c in CONDITIONAL_LIST}


PHRASES = []


for j, v in JOINERS.items():
    items = [j.format(i) for i in v]
    PHRASES.extend(items)


PHRASES.extend(CONDITIONALS)

for idiom in PHRASES:
    M_TOOL.add(
        'QBF',
        None,
        [
            {
                'LOWER': i.lower()
            } for i in OTHER_REPLACEMENTS
        ])


for idiom in PHRASES:
    M_TOOL.add(
        'QBF',
        None,
        [
            {
                'LOWER': i.lower()
            } for i in idiom.split(' ')
        ])


def replace_phrases(text):
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
    sentence = get_en_core_web_sm(text)

    phrase_matches = M_TOOL(sentence)

    replacements = []

    for _, start, end in phrase_matches:
        span = sentence[start:end]
        replacements.append(span)

    replacements = [f.text for f in spacy.util.filter_spans(replacements)]

    thetext = sentence.text

    for name in replacements:
        thetext = thetext.replace(
            name,
            name.replace(' ', '_')
        )

    for name in OTHER_REPLACEMENTS:
        if name in OTHER_REPLACEMENTS:
            thetext = thetext.replace(
                name,
                OTHER_REPLACEMENTS[name]
            )

    return thetext
