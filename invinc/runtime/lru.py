# Simple LRU implementation using linked list and dict.
# There are many recipes of this floating around; here's mine.

__all__ = [
    'LRUTracker',
]


class Node:
    
    __slots__ = ['val', 'prev', 'next']
    
    def __init__(self, val, prev=None, next=None):
        self.val = val
        self.prev = prev
        self.next = next

class LRUTracker:
    
    """A simple least-recently-used tracker. Operations
    are O(1) plus hashing. Elements must be hashable.
    """
    
    def __init__(self):
        self.head = self.tail = None
        self.map = {}
    
    def _prepend(self, node):
        if self.head is None:
            self.head = self.tail = node
        else:
            self.head.prev = node
            self.head = node
    
    def _unlink(self, node):
        if node.next is not None:
            node.next.prev = node.prev
        if node.prev is not None:
            node.prev.next = node.next
        if self.head == node:
            self.head = node.next
        if self.tail == node:
            self.tail = node.prev
    
    def add(self, val):
        assert val not in self.map
        node = Node(val, None, self.head)
        self.map[val] = node
        self._prepend(node)
    
    def remove(self, val):
        node = self.map.pop(val)
        self._unlink(node)
    
    def ping(self, val):
        node = self.map[val]
        self._unlink(node)
        self._prepend(node)
    
    def peek(self):
        return self.tail.val
    
    def pop(self):
        val = self.tail.val
        self.remove(val)
        return val
