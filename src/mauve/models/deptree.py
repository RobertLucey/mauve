from typing import (
    Mapping,
    Any,
    Iterable
)

from mauve.structure.conditional import CONDITIONAL_LIST
from mauve.constants import (
    ASSIGNMENT_WORDS,
    SENTENCE_TERMINATORS
)


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

    def serialize_line(self) -> str:
        return '%s   %s   %s   %s   %s' % (
            self.text.ljust(8),
            self.dep.ljust(8),
            self.head.ljust(8),
            self.pos.ljust(8),
            self.children
        )

    def serialize(self) -> Mapping[str, Any]:

        def serialize_children(children) -> Iterable[Mapping[str, Any]]:
            return [{
                'text': child.text,
                'dep': child.dep_,
                'head': child.head.text,
                'pos': child.head.pos,
                'idx': child.idx,
                'children': serialize_children(child.children)
            } for child in children]

        return {
            'text': self.text,
            'dep': self.dep,
            'head': self.head,
            'pos': self.pos,
            'children': serialize_children(self.children),
            'segment': self.segment.serialize(),
            'idx': self.idx
        }

    @staticmethod
    def get_empty_node():
        return DepNode('', '', '', '', [], 0)

    def get_clean(self):
        self.text = self.text.replace('_', ' ')
        return self


class DepTree():

    def __init__(self, nodes):
        self.nodes = nodes

    def join_words(self, multiword_list: Iterable[str]) -> None:
        """

        >>> [n.text for n in deptree.nodes]
        ['this', 'is', 'a', 'thing']
        >>> deptree.join_words(['a thing'])
        >>> [n.text for n in deptree.nodes]
        ['this', 'is', 'a thing']

        :param multiwordstr: list of wordy strings to join depnodes on
        """
        multiword_list = [words for words in multiword_list if ' ' in words]
        for multiwordstr in multiword_list:
            self.nodes = DepTree.replace_sub(
                self.nodes,
                multiwordstr.split(' '),
                [
                    DepNode(
                        multiwordstr,
                        '',
                        multiwordstr,
                        None,
                        [],
                        -1
                    )
                ]
            )
            self.reindex()

    def reindex(self) -> None:
        """
        Reindex nodes in the deptree for when the content changes
        """
        for idx, node in enumerate(self.nodes):
            if idx != 0:
                node.idx = self.nodes[idx - 1].idx + len(self.nodes[idx - 1].text) + 1
            else:
                node.idx = 0

    @staticmethod
    def find_sub_idx(
        original: Iterable[Any],
        repl_list: Iterable[Any],
        start=0
    ) -> tuple:
        """

        :param original: list to modify
        :repl_list: The list of items to replace
        :kwarg start: What idx to start from
        :return: The next idx of the start of the next occurance of repl_list
        """
        length = len(repl_list)
        for idx in range(start, len(original)):
            if [i.text for i in original[idx:idx + length]] == repl_list:
                return idx, idx + length

    @staticmethod
    def replace_sub(
        original: Iterable[Any],
        repl_list: Iterable[Any],
        new_list: Iterable[Any]
    ) -> Iterable[Any]:
        """
        Replace a subset of a list with some other subset

        Usage:
            >>> replace_sub([1,2,3,4], [2,3], [5,6])
            [1,5,6,4]

        :param original: list to modify
        :repl_list: The list of items to replace
        :param new_list: What to replace the repl_list with
        :return: original with repl_list replaced with new_list
        :rtype: list
        """
        length = len(new_list)
        idx = 0
        for start, end in iter(lambda: DepTree.find_sub_idx(original, repl_list, idx), None):
            original[start:end] = new_list
            idx = start + length
        return original

    def get_before_node(self, cmp_node: DepNode) -> Iterable[DepNode]:
        return [node for node in self.nodes if node.idx < cmp_node.idx]

    def get_after_node(
        self,
        cmp_node: DepNode,
        stop_at_punct=False
    ) -> Iterable[DepNode]:
        if stop_at_punct:
            try:
                first_punct = min([n.idx for n in self.nodes if n.text in SENTENCE_TERMINATORS and n.idx > cmp_node.idx])
                return [node for node in self.nodes if node.idx > cmp_node.idx and node.idx < first_punct]
            except:
                return [node for node in self.nodes if node.idx > cmp_node.idx]
        else:
            return [node for node in self.nodes if node.idx > cmp_node.idx]

    def get_closest_after(
        self,
        cmp_node: DepNode,
        dep=None,
        text=None
    ) -> DepNode:
        if dep is not None:
            try:
                return [
                    node for node in self.nodes if all([
                        node.idx > cmp_node.idx,
                        node.dep in dep
                    ])
                ][0]
            except IndexError:
                return DepNode.get_empty_node()
        if text is not None:
            try:
                return [
                    node for node in self.nodes if all([
                        node.idx > cmp_node.idx,
                        node.text in text
                    ])
                ][0]
            except IndexError:
                return DepNode.get_empty_node()

    def get_closest_before(
        self,
        cmp_node: DepNode,
        dep=None,
        text=None
    ) -> DepNode:
        if dep is not None:
            try:
                return [
                    node for node in self.nodes if all([
                        node.idx < cmp_node.idx,
                        node.dep in dep
                    ])
                ][-1]
            except IndexError:
                return DepNode.get_empty_node()

        if text is not None:
            try:
                return [
                    node for node in self.nodes if all([
                        node.idx < cmp_node.idx,
                        node.text in text
                    ])
                ][-1]
            except IndexError:
                return DepNode.get_empty_node()

    def serialize(self) -> Iterable[Mapping[str, str]]:
        return [n.serialize() for n in self.nodes]

    @property
    def equals(self):
        self.join_words(ASSIGNMENT_WORDS)

        # FIXME: Exclude things like 'what is' if the is we are using is
        # within the 'what is'

        return [node.get_clean() for node in self.nodes if node.text.lower().replace('_', ' ') in ASSIGNMENT_WORDS]

    @property
    def text(self) -> str:
        return ' '.join([n.text for n in self.nodes])

    @property
    def conditionals(self):
        self.join_words(CONDITIONAL_LIST)
        return [node.get_clean() for node in self.nodes if node.text.lower().replace('_', ' ') in CONDITIONAL_LIST]
