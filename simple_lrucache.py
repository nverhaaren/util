import functools
from collections import MutableMapping

from six import PY3


class SimpleLRUCache(MutableMapping):
    # Loosely based on Python 3 functools implementation
    class _HeadType(object):
        def __repr__(self):
            return '_Head'
    _Head = _HeadType()

    class Node(object):
        __slots__ = ['nxt', 'prv', 'key', 'value']

        def __init__(self, nxt, prv, key, value):
            self.nxt = nxt  # type: SimpleLRUCache.Node
            self.prv = prv  # type: SimpleLRUCache.Node
            self.key = key
            self.value = value

        @classmethod
        def head(cls):
            result = cls(None, None, SimpleLRUCache._Head, SimpleLRUCache._Head)
            result.nxt = result
            result.prv = result
            return result

        def unlink(self):
            self.nxt.prv = self.prv
            self.prv.nxt = self.nxt

        def insert_node_ahead(self, node):
            node.prv = self.prv
            node.nxt = self
            self.prv.nxt = node
            self.prv = node
            return node

        def insert_ahead(self, key, value):
            new = SimpleLRUCache.Node(self, self.prv, key, value)
            self.prv.nxt = new
            self.prv = new
            return new

    def __init__(self, size):
        assert self._size > 0
        self._size = size
        self._hash = {}
        self._dllist_head = self.Node.head()

    def __setitem__(self, key, value):
        assert key is not self._Head
        if key in self._hash:
            node = self._hash[key]
            node.unlink()
            node.value = value
            self._dllist_head.nxt.insert_node_ahead(node)
            return
        if len(self._hash) == self._size:
            last = self._dllist_head.prv
            del self._hash[last.key]
            last.unlink()
        new = self._dllist_head.nxt.insert_ahead(key, value)
        self._hash[key] = new

    def __delitem__(self, key):
        node = self._hash[key]
        node.unlink()
        del self._hash[key]

    def __getitem__(self, item):
        if item not in self._hash:
            raise KeyError(item)
        node = self._hash[item]
        node.unlink()
        self._dllist_head.nxt.insert_node_ahead(node)
        return node.value

    def __contains__(self, item):
        return item in self._hash

    def __len__(self):
        return len(self._hash)

    def __iter__(self):
        # If the consumer looks up values while iterating, that will mess with the linked list
        return iter(self._hash)

    def most_recent_keys(self):
        # Keys in order of most recent access
        result = []
        node = self._dllist_head.nxt
        while node.value is not self._Head:
            result.append(node.key)
            node = node.nxt
        return result

    if not PY3:
        keys = most_recent_keys


def memoize_lru(lru_cache):
    """
    :type lru_cache: MutableMapping
    :return: A decorator that memoizes a function using the provided lru_cache
    """
    # help avoid incorrect usage
    if not isinstance(lru_cache, MutableMapping):
        raise TypeError('Argument to memoize_lru must be MutableMapping; cannot decorate a function directly')

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            key = (args, frozenset((k, kwargs[k]) for k in sorted(kwargs)))
            if key not in lru_cache:
                lru_cache[key] = f(*args, **kwargs)
            return lru_cache[key]
        return wrapper
    return decorator
