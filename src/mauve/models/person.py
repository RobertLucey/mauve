from mauve import GENDER_DETECTOR

from mauve.models.entity import Entity


class Person(Entity):

    def __init__(self, *args, **kwargs):
        self.name = kwargs['name']

        kwargs.setdefault('etype', 'person')
        super(Person, self).__init__(*args, **kwargs)

    @property
    def gender(self):
        if not isinstance(self.name, str):
            return

        # TODO: if name is "Mr Jones" it should be obvious it's a male

        gender = None
        name_split = self.name.split(' ')

        title_map = {
            'mr': 'male',
            'mister': 'male',
            'mr.': 'male',
            'sir': 'male',
            'lady': 'female',
            'miss': 'female',
            'ms.': 'female',
            'mrs.': 'female',
            'ms': 'female',
            'mrs': 'female'
        }

        if name_split[0].lower() in title_map:
            return title_map[name_split[0].lower()]

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
