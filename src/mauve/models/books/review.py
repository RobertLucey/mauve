from mauve.models.generic import (
    GenericObject,
    GenericObjects
)


class Review(GenericObject):

    def __init__(self, *args, **kwargs):
        self.user = kwargs['user']
        self.score = kwargs['score']
        super(Review, self).__init__(*args, **kwargs)

    def serialize(self):
        return {
            'user': self.user,
            'score': self.score
        }


class Reviews(GenericObjects):

    def __init__(self, *args, **kwargs):
        kwargs['child_class'] = Review
        super(Reviews, self).__init__(*args, **kwargs)
