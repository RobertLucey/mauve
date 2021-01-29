from mauve.models.generic import (
    GenericObject,
    GenericObjects
)


class Tag(GenericObject):

    def __init__(self, *args, **kwargs):
        self.name = kwargs['name']
        super(Tag, self).__init__(*args, **kwargs)

    def serialize(self):
        return {
            'name': self.name
        }

    def add_book(self, book):
        """
        Add books to this tag,
        should be able to lazy load when we want to get the books back
        """
        raise NotImplementedError()


class Tags(GenericObjects):

    def __init__(self, *args, **kwargs):
        kwargs['child_class'] = Tag
        super(Tags, self).__init__(*args, **kwargs)

    def serialize(self):
        return [t.name for t in self]

    def contains(self, tag):
        """

        :param tag
        """
        if not isinstance(tag, Tag):
            tag = Tag(name=tag)

        # TODO: improve equality
        return tag.name.lower() in [t.name.lower() for t in self]
