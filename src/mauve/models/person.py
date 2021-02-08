from mauve import GENDER_DETECTOR
from mauve.phrases import replace_phrases
from mauve.models.entity import Entity
from mauve.models.generic import GenericObjects
from mauve.constants import (
    NAMES,
    NOT_NAMES,
    GENDER_PREFIXES,
    PERSON_TITLE_PREFIXES,
    PERSON_PREFIXES,
    PERSON_TRANSLATOR
)


class People(GenericObjects):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('child_class', Person)
        super(People, self).__init__(*args, **kwargs)

    def __contains__(self, person):
        name = person
        if isinstance(person, Person):
            name = person.name
        return name in [p.name for p in self]


class Person(Entity):

    def __init__(self, *args, **kwargs):
        """

        :kwarg: The person's name
        """
        self.name = kwargs['name'] if kwargs['name'] else ''

        if self.name.lower().startswith('the '):
            self.name = self.name[4:]

        if self.name in NOT_NAMES:
            self.name = ''

        if 'chapter' in self.name.lower():
            self.name = ''

        self.name = self.name.translate(PERSON_TRANSLATOR)
        self.name = self.name.strip()

        kwargs.setdefault('etype', 'person')
        super(Person, self).__init__(*args, **kwargs)

    def __hash__(self):
        return hash(self.name)

    def serialize(self):
        return {
            'name': self.name,
            'gender': self.gender
        }

    @property
    def gender(self):
        """
        Try to get the gender based on the name of the perosn

        :return: male or female
        """
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


def extract_people(sentence):
    """

    :param sentence:
    :return:
    :rtype: People
    """
    # Names can be chained by , and ands but we only get the last
    sentence.text = replace_phrases(sentence.text)
    people = People()

    # if a verb after something that could be a name or if X said then X is likely a person

    for segment in sentence.base_segments:
        text = segment.text.strip()

        # If the entity is defined as a person / it is Mr. Something
        if segment.tag == 'PERSON' or (
            segment.tag == 'dunno' and
            (
                any([text.lower().replace('_', ' ').startswith(prefix) for prefix in GENDER_PREFIXES])
            )
        ):
            person = Person(
                name=' '.join(
                    [
                        n for n in text.split(' ') if n[0].isupper() or n.lower() in PERSON_PREFIXES
                    ]
                )
            )
            people.append(person)
        elif 'minister' in text.lower():
            if any([
                'minister for ' in text.lower().replace('_', ' '),
                'minister of ' in text.lower().replace('_', ' ')
            ]):
                people.append(Person(name=text))
        else:
            # Do some stuff around caital letters
            if ' ' in text:
                split = text.split(' ')
                if any([
                    split[0] in NAMES,
                    split[0].lower() in GENDER_PREFIXES.keys(),
                    split[0].lower() in PERSON_TITLE_PREFIXES.keys(),

                    split[0][0].isupper()
                ]) and (
                    split[1][0].isupper()
                ):
                    people.append(Person(name=text))
            elif text in NAMES and text[0].isupper():
                people.append(Person(name=text))

    return people
