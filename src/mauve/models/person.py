import difflib
import logging
from typing import Iterable, Mapping, Any

from mauve import GENDER_DETECTOR
from mauve.preprocess.phrases import replace_phrases
from mauve.models.entity import Entity
from mauve.models.generic import GenericObjects
from mauve.constants.names import NAMES
from mauve.constants import (
    EXTRA_MALE_NAMES,
    EXTRA_FEMALE_NAMES,
    AUTHOR_METADATA,
    MALE_WORDS,
    FEMALE_WORDS,
    NOT_NAMES,
    GENDER_PREFIXES,
    PERSON_TITLE_PREFIXES,
    PERSON_PREFIXES,
    PERSON_TRANSLATOR,
    EXTENDED_PUNCTUATION,
    LIKELY_PERSON_PREFIXES
)

logger = logging.getLogger('mauve')


def clean_name(name: str) -> str:
    """
    Clean up a name by removing parts we don't care about or set
    to empty if the name is untrustworthy.

    Usage:
        >>> clean_name('Doctor Cat')
        'Cat'
        >>> clean_name('The Cat')
        'Cat'
        >>> clean_name('Cat')
        'Cat'

    :param name: A string of a name or loose name
    :return: A name with unnecessary parts removed
    :rtype: str
    """

    whitelisted_names = {'I', 'he', 'she', 'He', 'She'}
    if name in whitelisted_names:
        logger.debug('Not cleaning name \'%s\'', name)
        return name

    mod_name = ' '.join(
        [
            c for c in name.split(' ') if all(
                [
                    c not in EXTENDED_PUNCTUATION,
                    c.lower().replace('.', '') not in LIKELY_PERSON_PREFIXES
                ]
            )
        ]
    ).strip()

    if mod_name.lower().startswith('the '):
        mod_name = mod_name[4:]

    if mod_name.lower().startswith('a '):
        mod_name = mod_name[2:]

    if any(
        [
            mod_name in NOT_NAMES,
            'chapter' in [n.lower() for n in mod_name.split()],
            'part' in [n.lower() for n in mod_name.split()],
            'section' in [n.lower() for n in mod_name.split()],
        ]
    ):
        mod_name = ''

    mod_name = mod_name.translate(PERSON_TRANSLATOR).replace('\n', ' ').replace('  ', ' ').strip()

    if name != mod_name:
        logger.debug('Cleaned name \'%s\' => \'%s\'', name, mod_name)

    return mod_name


class People(GenericObjects):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('child_class', Person)
        super(People, self).__init__(*args, **kwargs)

    def __contains__(self, person) -> bool:
        if not isinstance(person, Person):
            person = Person(name=person)
        return any([p.is_similar_to(person) for p in self])

    def append(self, obj) -> None:
        if not isinstance(obj, self.child_class):
            raise TypeError('Bad type: %s' % (type(obj)))

        if any([obj.name == i.name for i in self]):
            for person in self:
                if person.name == obj.name:
                    person.inc_references()
        else:
            obj.inc_references()
            self._data.append(obj)

    def get_trustworthy_people(self) -> Iterable:
        return [person for person in self if person.is_trustworthy]

    def get_count_of(self, person) -> int:
        if isinstance(person, str):
            person = Person(name=person)
        return len([person.name for person in self if person.name == person.name])

    def remove_near_duplicates(self) -> None:
        """
        Replace near name duplicates with the more commonly used
        variant. Also sum the references into the more commonly
        used name.
        """
        to_remove = []
        for base in self:
            for comparison in self:
                if base == comparison:
                    continue
                if base.is_similar_to(comparison):
                    if self.get_count_of(base) > self.get_count_of(comparison):
                        comparison.dirty_name = base.dirty_name
                        comparison.references += base.references
                        logger.debug('Removing near duplicate name \'%s\' \'%s\'', base.name, comparison.name)
                        to_remove.append(base)
                    else:
                        base.dirty_name = comparison.dirty_name
                        base.references += comparison.references
                        logger.debug('Removing near duplicate name \'%s\' \'%s\'', base.name, comparison.name)
                        to_remove.append(comparison)

        for person in to_remove:
            self.remove(person)


class Person(Entity):

    def __init__(self, *args, **kwargs):
        """

        :kwarg name: The person / character's name
        :kwarg trustworthy:
        :kwarg references: The number of references made to this person
        """
        self.dirty_name = kwargs['name'] if kwargs['name'] else ''
        self.trustworthy = kwargs.get('trustworthy', True)
        self.references = kwargs.get('trustworthy', 0)

        kwargs.setdefault('etype', 'person')
        super(Person, self).__init__(*args, **kwargs)

    def __hash__(self):
        return hash(self.name)

    def is_similar_to(self, cmp_person) -> bool:
        """
        Return if a person is similar enough to this person
        This is based on the cleaned name

        :param cmp_person: Person object to compare to
        """

        def matches(first_string, second_string):
            seqmatcher = difflib.SequenceMatcher(None, first_string, second_string)
            return [first_string[i:i+n] for i, _, n in seqmatcher.get_matching_blocks() if n > 0]

        if self.name.lower() == cmp_person.name.lower():
            return True

        # If one has a name that is the last part of a split they
        #     should be the same person
        # Hyde == Edward Hyde

        # FIXME this dups items need to merge occurances or whatever they're called
        if ' ' in self.name and ' ' not in cmp_person.name:
            if self.name.split(' ')[-1].lower() == cmp_person.name.lower():
                return True

        try:
            if max([
                len(m) for m in matches(
                    self.name.lower(),
                    cmp_person.name.lower()
                )
            ]) > max([
                len(self.name.lower()),
                len(cmp_person.name.lower())
            ]) / 1.5 and min([
                len(self.name.lower()),
                len(cmp_person.name.lower())
            ]) > 3:
                return True
        except:
            return False

        return False

    def inc_references(self) -> None:
        self.references += 1

    def serialize(self) -> Mapping[str, str]:
        return {
            'name': self.name,
            'gender': self.gender
        }

    @property
    def gender(self) -> str:
        """
        Try to get the gender based on the name of the perosn

        :return: male, female or None
        """
        if not isinstance(self.name, str):
            logger.debug('Cannot get gender for \'%s\'', self.name)
            return

        if self.name in MALE_WORDS:
            logger.debug('Gender \'%s\' is \'%s\'', self.name, 'male')
            return 'male'
        elif self.name in FEMALE_WORDS:
            logger.debug('Gender \'%s\' is \'%s\'', self.name, 'female')
            return 'female'

        # TODO: if name is "Mr Jones" it should be obvious it's a male

        gender = None
        name_split = self.dirty_name.split(' ')

        if name_split[0] in EXTRA_MALE_NAMES:
            logger.debug('Gender \'%s\' is \'%s\'', self.name, 'male')
            return 'male'
        elif name_split[0] in EXTRA_FEMALE_NAMES:
            logger.debug('Gender \'%s\' is \'%s\'', self.name, 'female')
            return 'female'

        if name_split[0].lower() in GENDER_PREFIXES.keys():
            logger.debug('Gender \'%s\' is \'%s\'', self.name, GENDER_PREFIXES[name_split[0].lower()])
            return GENDER_PREFIXES[name_split[0].lower()]

        if '.' in name_split[0]:
            # Should attempt to do something here
            gender = None
        elif ' and ' in self.dirty_name.lower() or '&' in self.dirty_name.lower():
            # more than one person, should do something about this before it gets here
            gender = None
        else:
            gender = GENDER_DETECTOR.get_gender(name_split[0])
            if gender != 'male' and gender != 'female':
                gender = GENDER_DETECTOR.get_gender(self.name)
                if gender != 'male' and gender != 'female':
                    gender = GENDER_DETECTOR.get_gender(self.dirty_name)

        if gender in {'unknown', 'andy'}:
            gender = None

        if gender:
            logger.debug('Gender \'%s\' is \'%s\'', self.name, gender)
        else:
            logger.debug('Cannot get gender for \'%s\'', self.name)

        return gender

    @property
    def is_trustworthy(self) -> bool:
        # TODO: can do some more bits from the name I guess
        is_trustworthy = self.trustworthy or self.references > 2
        logger.debug('Person \'%s\' trustworthy: %s', self.name, is_trustworthy)
        return is_trustworthy

    @property
    def name(self) -> str:
        """
        Get the cleaned name of the person
        """
        return clean_name(self.dirty_name)


class Author(Person):

    @property
    def nationality(self) -> str:
        if self.name in AUTHOR_METADATA:
            nationality = AUTHOR_METADATA[self.name]['nationality']
            if nationality is not None:
                return nationality.replace('\n', ' ').replace('  ', ' ').strip()

        if len(self.name.split(' ')) > 2:
            first_last = '%s %s' % (self.name.split(' ')[0], self.name.split(' ')[-1])
            if first_last in AUTHOR_METADATA:
                nationality = AUTHOR_METADATA[first_last]['nationality']
                if nationality is not None:
                    return nationality.replace('\n', ' ').replace('  ', ' ').strip()

        return None

    @property
    def birth_year(self) -> int:
        if self.name in AUTHOR_METADATA:
            return AUTHOR_METADATA[self.name]['born']
        return None

    def serialize(self) -> Mapping[str, Any]:
        data = super(Author, self).serialize()
        data.update(
            {
                'nationality': self.nationality,
                'birth_year': self.birth_year
            }
        )
        return data


def extract_people(sentence) -> People:
    """
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
            if not person.name.replace(' ', '').isupper():
                people.append(person)
        elif 'minister' in text.lower():
            if any([
                'minister for ' in text.lower().replace('_', ' '),
                'minister of ' in text.lower().replace('_', ' ')
            ]):
                people.append(Person(name=text))
        else:
            # Do some stuff around caital letters
            text = text.replace('  ', ' ')
            if ' ' in text:
                split = text.split(' ')
                if any([
                    split[0] in NAMES,
                    split[0].lower() in GENDER_PREFIXES.keys(),
                    split[0].lower() in PERSON_TITLE_PREFIXES.keys(),
                ]) and (
                    split[1][0].isupper()
                ):
                    if not text.replace(' ', '').isupper():
                        people.append(Person(name=text))
                elif any([
                    split[0] in NAMES,
                    split[0].lower() in GENDER_PREFIXES.keys(),
                    split[0].lower() in PERSON_TITLE_PREFIXES.keys(),

                    split[0][0].isupper()
                ]) and (
                    split[1][0].isupper()
                ):
                    if not text.replace(' ', '').isupper():
                        people.append(Person(name=text))

            elif text in NAMES and text[0].isupper():
                people.append(Person(name=text))

    return people
