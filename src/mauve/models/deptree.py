from mauve.structure.conditional import CONDITIONAL_LIST
from mauve.constants import ASSIGNMENT_WORDS


def serialize_children(children):
    return [{
        'text': child.text,
        'dep': child.dep_,
        'head': child.head.text,
        'pos': child.head.pos,
        'idx': child.idx,
        'children': serialize_children(child.children)
    } for child in children]


class DepNode:

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

    def join_words(self, multiword_list):
        for multiwordstr in multiword_list:
            dn = DepNode(
                multiwordstr,
                '',
                multiwordstr,
                None,
                [],
                -1
            )

            self.nodes = self.replace_sub(self.nodes, multiwordstr.split(' '), [dn])
            self.reindex()

    def reindex(self):
        for idx, node in enumerate(self.nodes):
            node.idx = idx

    def find_sub_idx(self, original, repl_list, start=0):
        length = len(repl_list)
        for idx in range(start, len(original)):
            if [i.text for i in original[idx:idx + length]] == repl_list:
                return idx, idx + length

    def replace_sub(self, original, repl_list, new_list):
        """
        Replace a subset of a list with some other subset
        >> replace_sub([1,2,3,4], [2,3], [5,6])
        [1,5,6,4]
        """
        length = len(new_list)
        idx = 0
        for start, end in iter(lambda: self.find_sub_idx(original, repl_list, idx), None):
            original[start:end] = new_list
            idx = start + length
        return original

    def get_before_node(self, cmp_node):
        return [node for node in self.nodes if node.idx < cmp_node.idx]

    def get_after_node(self, cmp_node, stop_at_punct=False):
        if stop_at_punct:
            try:
                first_punct = min([n.idx for n in self.nodes if n.text in ['!', '.', '?'] and n.idx > cmp_node.idx])
                return [node for node in self.nodes if node.idx > cmp_node.idx and node.idx < first_punct]
            except:
                return [node for node in self.nodes if node.idx > cmp_node.idx]
        else:
            return [node for node in self.nodes if node.idx > cmp_node.idx]


    def get_closest_after(self, cmp_node, dep=None, text=None):
        if dep is not None:
            try:
                return [node for node in self.nodes if node.idx > cmp_node.idx and node.dep in dep][0]
            except IndexError:
                return DepNode.get_empty_node()
        if text is not None:
            try:
                return [node for node in self.nodes if node.idx > cmp_node.idx and node.text in text][0]
            except IndexError:
                return DepNode.get_empty_node()

    def get_closest_before(self, cmp_node, dep=None, text=None):
        if dep is not None:
            try:
                return [node for node in self.nodes if node.idx < cmp_node.idx and node.dep in dep][-1]
            except IndexError:
                return DepNode.get_empty_node()

        if text is not None:
            try:
                return [node for node in self.nodes if node.idx < cmp_node.idx and node.text in text][-1]
            except IndexError:
                return DepNode.get_empty_node()

    def serialize(self):
        return [n.serialize() for n in self.nodes]

    @property
    def equals(self):
        return [node for node in self.nodes if node.text in ASSIGNMENT_WORDS]

    @property
    def text(self):
        return ' '.join([n.text for n in self.nodes])

    @property
    def conditionals(self):  # prob move this to sentence... and then move to segments
        return [node for node in self.nodes if node.text.lower() in CONDITIONAL_LIST]
