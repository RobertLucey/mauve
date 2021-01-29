from mauve.models.assignment import extract_assignments
from mauve.models.meaning_tree import Node

def update(n, r):
    if r is not None:
        n.child = r
    return n

def get_back(assignment_node):
    if assignment_node == None:
        return Node(None)
    else:

        extraction = extract_assignments(
            assignment_node.right,
            get_node=True
        )

        if extraction.is_empty:
            return Node(None)

        if extraction.value == None:
            return Node(None)

        if extraction.left is not None:
            assignment_node.left = extraction.left

        if extraction.value is not None:
            assignment_node.value = extraction.value

        if extraction.right is not None:
            assignment_node.right = extraction.right

        t = get_back(extraction)
        if t:
            assignment_node.child = t

        return assignment_node
