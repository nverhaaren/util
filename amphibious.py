class AttrDict(dict):
    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError('AttrDict has no attribute {!r}'.format(item))

    def __setattr__(self, key, value):
        try:
            super(AttrDict, self).__getattribute__(key)
        except AttributeError:
            self[key] = value
        else:
            super(AttrDict, self).__setattr__(key, value)

    def __delattr__(self, item):
        try:
            super(AttrDict, self).__getattribute__(item)
        except AttributeError:
            del self[item]
        else:
            super(AttrDict, self).__delattr__(item)


class KeyedBunch(object):
    def __getitem__(self, item):
        if not isinstance(item, str) or item.startswith('__'):
            raise KeyError('KeyedBunch has no key {!r}'.format(item))
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError('KeyedBunch has no key {!r}'.format(item))

    def __setitem__(self, key, value):
        if not isinstance(key, str) or key.startswith('__'):
            raise KeyError('Cannot set key {!r}'.format(key))
        setattr(self, key, value)

    def __delitem__(self, key):
        if not isinstance(key, str) or key.startswith('__'):
            raise KeyError('Cannot delete key {!r}'.format(key))
        try:
            delattr(self, key)
        except AttributeError:
            raise KeyError('KeyedBunch has no key {!r}'.format(key))
