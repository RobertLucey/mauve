
APPROSTROPHES = ['’', '\'']
CONTRACTION_MAP = {
    '\'aight': 'alright',
    'ain\'t': 'is not',
    'amn\'t': 'am not',
    'aren\'t': 'are not',
    'can\'t': 'cannot',
    '\'cause': 'because',
    'could\'ve': 'could have',
    'couldn\'t': 'could not',
    'couldn\'t\'ve': 'could not have',
    'daren\'t': 'dare not',
    'daresn\'t': 'dare not',
    'dasn\'t': 'dare not',
    'didn\'t': 'did not',
    'doesn\'t': 'does not',
    'don\'t': 'do not',
    'dunno': 'do not know',
    'd\'ye': 'do you',
    'e\'er': 'ever',
    '\'em': 'them',
    'everybody\'s': 'everybody is',
    'everyone\'s': 'everyone is',
    'finna': 'going to',
    'g\'day': 'good day',
    'gimme': 'give me',
    'giv\'n': 'given',
    'gonna': 'going to',
    'gon\'t': 'go not',
    'gotta': 'got to',
    'hadn\'t': 'had not',
    'had\'ve': 'had have',
    'hasn\'t': 'has not',
    'haven\'t': 'have not',
    'he\'d': 'he had',
    'he\'ll': 'he will',
    'he\'s': 'he is',
    'here\'s': 'here is',
    'he\'ve': 'he have',
    'how\'d': 'how did',
    'how\'ll': 'how will',
    'how\'re': 'how are',
    'how\'s': 'how is',
    'I\'d': 'I would',
    'I\'d\'ve': 'I would have',
    'I\'ll': 'I will',
    'I\'m': 'I am',
    'I\'m\'a': 'I am about to',
    'I\'m\'o': 'I am going to',
    'innit': 'is it not',
    'I\'ve': 'I have',
    'isn\'t': 'is not',
    'it\'d': 'it would',
    'it\'ll': 'it will',
    'it\'s': 'it is',
    'iunno': 'I don\'t know',
    'kinda': 'kind of',
    'let\'s': 'let us',
    'ma\'am': 'madam',
    'mayn\'t': 'may not',
    'may\'ve': 'may have',
    'methinks': 'me thinks',
    'mightn\'t': 'might not',
    'might\'ve': 'might have',
    'mustn\'t': 'must not',
    'mustn\'t\'ve': 'must not have',
    'must\'ve': 'must have',
    'needn\'t': 'need not',
    'nal': 'and all',
    'ne\'er': 'never',
    'o\'clock': 'of the clock',
    'o\'er': 'over',
    'ol\'': 'old',
    'oughtn\'t': 'ought not',
    'shalln\'t': 'shall not',
    'shan\'t': 'shall not',
    'she\'d': 'she would',
    'she\'ll': 'she will',
    'she\'s': 'she is',
    'should\'ve': 'should have',
    'shouldn\'t': 'should not',
    'shouldn\'t\'ve': 'should not have',
    'somebody\'s': 'somebody is',
    'someone\'s': 'someone is',
    'something\'s': 'something is',
    'so\'re': 'so are',
    'that\'ll': 'that will',
    'that\'re': 'that are',
    'that\'s': 'that is',
    'that\'d': 'that would',
    'there\'d': 'there would',
    'there\'ll': 'there will',
    'there\'re': 'there are',
    'there\'s': 'there is',
    'these\'re': 'these are',
    'these\'ve': 'these have',
    'they\'d': 'they would',
    'they\'ll': 'they will',
    'they\'re': 'they are',
    'they\'ve': 'they have',
    'this\'s': 'this is',
    'those\'re': 'those are',
    'those\'ve': 'those have',
    '\'tis': 'it is',
    'to\'ve': 'to have',
    '\'twas': 'it was',
    'wanna': 'want to',
    'wasn\'t': 'was not',
    'we\'d': 'we would',
    'we\'d\'ve': 'we would have',
    'we\'ll': 'we will',
    'we\'re': 'we are',
    'we\'ve': 'we have',
    'weren\'t': 'were not',
    'what\'d': 'what did',
    'what\'ll': 'what will',
    'what\'re': 'what are',
    'what\'s': 'what is',
    'what\'ve': 'what have',
    'when\'s': 'when is',
    'where\'d': 'where did',
    'where\'ll': 'where will',
    'where\'re': 'where are',
    'where\'s': 'where is',
    'where\'ve': 'where have',
    'which\'d': 'which would',
    'which\'ll': 'which will',
    'which\'re': 'which are',
    'which\'s': 'which is',
    'which\'ve': 'which have',
    'who\'d': 'who would',
    'who\'d\'ve': 'who would have',
    'who\'ll': 'who will',
    'who\'re': 'who are',
    'who\'s': 'who is',
    'who\'ve': 'who have',
    'why\'d': 'why did',
    'why\'re': 'why are',
    'why\'s': 'why is',
    'willn\'t': 'will not',
    'won\'t': 'will not',
    'wonnot': 'will not',
    'would\'ve': 'would have',
    'wouldn\'t': 'would not',
    'wouldn\'t\'ve': 'would not have',
    'y\'all': 'you all',
    'y\'all\'d\'ve': 'you all would have',
    'y\'all\'d\'n\'ve': 'you all would not have',
    'y\'all\'re': 'you all are',
    'y\'at': 'you at',
    'you\'d': 'you would',
    'you\'ll': 'you will',
    'you\'re': 'you are',
    'you\'ve': 'you have',
}


def replace_contractions(content):
    for k, replacement in CONTRACTION_MAP.items():
        for appos in APPROSTROPHES:
            find = k.replace('\'', appos)
            content = content.replace(find, replacement)
    return content