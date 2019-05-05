class Extractor(object):
    def __init__(self, fns=None):
        self.__fns = fns if fns is not None else []

    def __getattr__(self, item):
        return Extractor(self.__fns + [lambda x: getattr(x, item)])

    def __getitem__(self, item):
        return Extractor(self.__fns + [lambda x: x[item]])

    def __call__(self, *args, **kwargs):
        if not len(args) == 1 and len(kwargs) == 0:
            raise TypeError('Extractor not called with a single positional argument')

        ret = args[0]
        for fn in self.__fns:
            ret = fn(ret)

        return ret


extract = Extractor()
