class Node:

    def __init__(self, value):
        self._left = None
        self._right = None
        self._child = None
        self.value = value

    @property
    def child(self):
        return self._child

    @child.setter
    def child(self, node):
        print(type(node))
        assert(isinstance(node, Node))
        self._child = node

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, node):
        assert(isinstance(node, Node))
        self._left = node

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, node):
        assert(isinstance(node, Node))
        self._right = node

    def serialize(self):
        return {
            'left': self.left.serialize() if self.left else None,
            'right': self.right.serialize() if self.right else None,
            'value': self.value.serialize() if hasattr(self.value, 'serialize') else self.value
        }

    @property
    def is_empty(self):
        return all([
            self.left is None,
            self.right is None,
            self.value is None
        ])

    def serialize(self):
        return (
            self.left.text,
            self.value.text,
            self.right.text
        )

    @property
    def text(self):
        return ' '.join([
            self.left.text if self.left else '',
            self.value.text if self.value else '',
            self.right.text if self.right else '',
            '[' + self.child.text + ']' if self.child else ''
        ]).strip()
