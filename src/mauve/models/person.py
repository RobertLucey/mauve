from mauve import GENDER_DETECTOR

from mauve.models.entity import Entity

from mauve.constants import GENDER_PREFIXES


class Person(Entity):

    def __init__(self, *args, **kwargs):
        '''

        :kwarg: The person's name
        '''
        self.name = kwargs['name']

        if self.name.lower().startswith('the '):
            self.name = self.name[4:]

        wrongs = [
            'My',
            'An',
            'don',
            'Him',
            'Her',
            'So',
            'Don'
        ]

        if self.name in wrongs:
            self.name = ''

        if 'chapter' in self.name.lower():
            self.name = ''

        kwargs.setdefault('etype', 'person')
        super(Person, self).__init__(*args, **kwargs)

    @property
    def gender(self):
        if not isinstance(self.name, str):
            return

        # TODO: if name is "Mr Jones" it should be obvious it's a male

        gender = None
        name_split = self.name.split(' ')

        if name_split[0].lower() in GENDER_PREFIXES.keys():
            return GENDER_PREFIXES[name_split[0].lower()]

        if '.' in name_split[0]:
            # Should attempt to do something here
            gender = None
        elif ' and ' in self.name.lower() or '&' in self.name.lower():
            # more than one person, should do something about this before it gets here
            gender = None
        else:
            gender = GENDER_DETECTOR.get_gender(name_split[0])
            if gender != 'male' and gender != 'female':
                gender = None

        return gender
