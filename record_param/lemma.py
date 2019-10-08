def find_nested_index(nested, val, iterable_cls=list):
    try:
        return [nested.index(val)]
    except ValueError:
        for idx, val_ in enumerate(nested):
            if not isinstance(val_, iterable_cls):
                continue
            try:
                return [idx] + find_nested_index(val_, val)
            except ValueError:
                pass
        raise ValueError('{!r} not in nested list'.format(val))


def at_nested_index(nested, idx):
    if len(idx) == 1:
        return nested[idx[0]]
    return at_nested_index(nested[idx[0]], idx[1:])
