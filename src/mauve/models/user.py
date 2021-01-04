from mauve.models.generic import (
    GenericObject,
    GenericObjects
)


class User(GenericObject):

    def __init__(self, *args, **kwargs):
        self.site = kwargs.get('site', None)
        self.reviews = kwargs.get('reviews', None)
        super(User, self).__init__(*args, **kwargs)

    def serialize(self):
        return {
            'reviews': self.reviews,
            'site': self.site,
            'id': self.id
        }


class Users(GenericObjects):

    def __init__(self, *args, **kwargs):
        kwargs['child_class'] = User
        super(Users, self).__init__(*args, **kwargs)
