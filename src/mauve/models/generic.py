import uuid


class GenericObjects(object):

    def __init__(self, *args, **kwargs):
        '''

        :kwarg data:
        :kwarg child_class:
        '''
        self._data = kwargs.get('data', [])
        self.child_class = kwargs.get('child_class', GenericObject)

    def __getitem__(self, i):
        return self._data[i]

    def __iter__(self):
        return (i for i in self._data)

    def __len__(self):
        return len(self._data)

    def append(self, obj):
        '''

        :param obj:
        '''
        if not isinstance(obj, self.child_class):
            raise TypeError('Bad type: %s' % (type(obj)))
        self._data.append(obj)

    def extend(self, objs):
        '''

        :param objs:
        '''
        for obj in objs:
            self.append(obj)

    def serialize(self):
        return [obj.serialize() for obj in self.data]

    def reload(self):
        '''
        Reload to get rid of object cached properties. This should be done on
        any modifications to the data within any of the object's objects.
        '''
        self._data = [
            self.child_class(data=obj.data) for obj in self.data if len(obj.data) > 0
        ]

    def remove(self, obj):
        if not isinstance(obj, self.child_class):
            raise TypeError('Bad type: %s' % (type(obj)))
        self._data = [
            o for o in self._data if o.id != obj.id
        ]

    @property
    def data(self):
        return self._data


class GenericObject(object):

    def __init__(self, *args, **kwargs):
        '''

        :kwarg data:
        '''
        self.id = kwargs.get('id', uuid.uuid4())

    def __repr__(self):
        return str('%s(%s)' % (
            type(self).__name__,
            self.id
        ))

    def serialize(self):
        raise NotImplementedError()
