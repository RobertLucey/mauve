import spacy
from spacy.matcher import Matcher

nlp = spacy.load('en_core_web_lg')
m_tool = Matcher(nlp.vocab)


other_replacements = {
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
    'i\'m': 'i am',
    'a great deal': 'a lot',
    'fully aware': 'aware',
    'motor car': 'car'
}  # TODO: test this


bodies = [
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

joiners = {
    'department of {}': bodies,
    'minister for {}': bodies,
    'minister of {}': bodies,
}


PHRASES = []


for j, v in joiners.items():
    items = [j.format(i) for i in v]
    PHRASES.extend(items)



for idiom in PHRASES:
    m_tool.add(
        'QBF',
        None,
        [
            {
                'LOWER': i.lower()
            } for i in other_replacements
        ])


for idiom in PHRASES:
    m_tool.add(
        'QBF',
        None,
        [
            {
                'LOWER': i.lower()
            } for i in idiom.split(' ')
        ])


def replace_phrases(text):

    sentence = nlp(text.lower())

    phrase_matches = m_tool(sentence)

    replacements = []

    for match_id, start, end in phrase_matches:
        span = sentence[start:end]
        replacements.append(span)

    replacements = [f.text for f in spacy.util.filter_spans(replacements)]

    thetext = sentence.text

    sub_replace = list(set([s.text for s in sentence.ents]))

    for name in replacements + sub_replace:

        thetext = thetext.replace(
            name,
            name.replace(' ', '_')
        )

    for name in other_replacements:
        if name in other_replacements:
            thetext = thetext.replace(
                name,
                other_replacements[name]
            )

    return thetext
