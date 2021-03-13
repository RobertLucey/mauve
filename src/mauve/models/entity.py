from mauve.models.generic import GenericObject


class Entity(GenericObject):

    def __init__(self, *args, **kwargs):
        self.etype = kwargs.get('etype', None)
        super(Entity, self).__init__(*args, **kwargs)
