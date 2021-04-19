from typing import (
    Any,
    Iterable
)


class Node(object):
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.count = 1

    def __str__(self) -> str:
        return 'value: {0}, count: {1}'.format(self.value, self.count)


def insert(root: Node, value: Any) -> Node:
    if not root:
        return Node(value)
    elif root.value == value:
        root.count += 1
    elif value < root.value:
        root.left = insert(root.left, value)
    else:
        root.right = insert(root.right, value)

    return root


def create(seq: Iterable) -> Node:
    root = None
    for word in seq:
        root = insert(root, word)

    return root


def search(root: Node, word: str, depth=1) -> tuple[int, int]:
    if not root:
        return 0, 0
    elif root.value == word:
        return depth, root.count
    elif word < root.value:
        return search(root.left, word, depth + 1)
    return search(root.right, word, depth + 1)
