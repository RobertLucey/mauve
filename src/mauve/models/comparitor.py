TENSE_MAP = {
    'is': 'present',
    'are': 'present',
    'am': 'present',
    'be': 'present',
    'was': 'past',
    'were': 'past',
    'will be': 'future',
    'can be': 'conditional_present',
    'could be': 'conditional_present'
}

TENSE_VALUE_MAP = {
    'past': -1,
    'present': 0,
    'future': 1,
    'conditional_present': -0.5
}


class Comparitor():
    """
    For things like is / was
    """

    def __init__(self, text: str):
        self.text = text

    def __lt__(self, cmp_obj):
        assert(isinstance(cmp_obj, Comparitor))
        return TENSE_VALUE_MAP[self.tense] < TENSE_VALUE_MAP[cmp_obj.tense]

    @property
    def tense(self) -> str:
        return TENSE_MAP[self.text.lower().replace('___', ' ').replace('_', ' ')]
