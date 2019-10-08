class AttrDict(dict):
    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError('AttrDict has not attribute {!r}'.format(item))

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
