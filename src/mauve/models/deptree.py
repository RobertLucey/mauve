


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
        from mauve.models.text import Segment
        return Segment(
            self.text,
            tag=self.pos
        )

    def serialize_line(self):
        return '%s   %s   %s   %s   %s' % (self.text.ljust(8), self.dep.ljust(8), self.head.ljust(8), self.pos.ljust(8), self.children)


class DepTree():

    def __init__(self, nodes):
        self.nodes = nodes

    def get_after_node(self, cmp_node):
        return [node for node in self.nodes if node.idx > cmp_node.idx]

    @property
    def equals(self):
        eqs = ['is', 'are', 'am', 'was', 'were', 'be']
        return [node for node in self.nodes if node.text in eqs]

    @property
    def root(self):
        try:
            return [node for node in self.nodes if node.dep == 'ROOT'][0]
        except IndexError:
            return DepNode('', '', '', '', [], 0)

    @property
    def dobj(self):
        try:
            return [node for node in self.nodes if node.dep == 'dobj'][0]
        except IndexError:
            return DepNode('', '', '', '', [], 0)

    @property
    def nsubj(self):
        try:
            return [node for node in self.nodes if node.dep == 'nsubj'][0]
        except IndexError:
            return DepNode('', '', '', '', [], 0)

    @property
    def post_root(self):
        idx = max([idx if x.dep == 'ROOT' else -1 for idx, x in enumerate(self.nodes)])
        return self.nodes[idx + 1:]

    @property
    def text(self):
        return ' '.join([n.text for n in self.nodes])

    def closest_before(self, cmp_node, dep=None):
        try:
            return [node for node in self.nodes if node.idx < cmp_node.idx and node.dep in dep][-1]
        except IndexError:
            return DepNode('', '', '', '', [], 0)
