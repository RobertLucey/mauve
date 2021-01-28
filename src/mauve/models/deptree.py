

def serialize_children(children):
    return [{
        'text': child.text,
        'dep': child.dep_,
        'head': child.head.text,
        'pos': child.head.pos,
        'idx': child.idx,
        'children': serialize_children(child.children)
    } for child in children]



class DepNode():

    def __init__(self, text, dep, head, pos, children, idx):
        self.text = text
        self.dep = dep
        self.head = head
        self.pos = pos
        self.children = children
        self.idx = idx

    @property
    def segment(self):
        from mauve.models.segment import Segment
        return Segment(
            self.text,
            tag=self.pos
        )

    def serialize_line(self):
        return '%s   %s   %s   %s   %s' % (self.text.ljust(8), self.dep.ljust(8), self.head.ljust(8), self.pos.ljust(8), self.children)

    def serialize(self):
        return {
            'text': self.text,
            'dep': self.dep,
            'head': self.head,
            'pos': self.pos,
            'children': serialize_children(self.children),
            'segment': self.segment.serialize()
        }

    @staticmethod
    def get_empty_node():
        return DepNode('', '', '', '', [], 0)


class DepTree():

    def __init__(self, nodes):
        self.nodes = nodes

    def get_after_node(self, cmp_node):
        return [node for node in self.nodes if node.idx > cmp_node.idx]

    def get_closest_before(self, cmp_node, dep=None):
        try:
            return [node for node in self.nodes if node.idx < cmp_node.idx and node.dep in dep][-1]
        except IndexError:
            return DepNode.get_empty_node()

    def serialize(self):
        return [n.serialize() for n in self.nodes]

    @property
    def equals(self):
        eqs = ['is', 'are', 'am', 'was', 'were', 'be']
        return [node for node in self.nodes if node.text in eqs]

    @property
    def text(self):
        return ' '.join([n.text for n in self.nodes])
