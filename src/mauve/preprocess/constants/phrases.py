from spacy.matcher import Matcher

from mauve.structure.conditional import CONDITIONAL_LIST
from mauve import ENCORE_LG
from mauve.preprocess.constants.replacements import REPLACEMENTS


PHRASE_MATCHER = Matcher(ENCORE_LG.vocab)


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
    PHRASE_MATCHER.add(
        'QBF',
        None,
        [
            {
                'LOWER': i.lower()
            } for i in REPLACEMENTS
        ])


for idiom in PHRASES:
    PHRASE_MATCHER.add(
        'QBF',
        None,
        [
            {
                'LOWER': i.lower()
            } for i in idiom.split(' ')
        ])
