import re

from mauve.models.person import Person


class Speaker(Person):

    def __init__(self, dirty_name, **kwargs):
        kwargs.setdefault('name', dirty_name)
        super(Speaker, self).__init__(dirty_name, **kwargs)

    def serialize(self):
        serialization = super(Speaker, self).serialize()
        serialization.update(
            {
                'role': None  # TODO
            }
        )
        return serialization

    @property
    def name(self):
        cleaned_name = ' '.join(
            re.findall(
                '[A-Z][^A-Z]*',
                self.dirty_name.replace(' ', '').replace('#', '')
            )
        )
        if not cleaned_name:
            cleaned_name = self.dirty_name.replace(' ', '').replace('#', '')

        return cleaned_name
