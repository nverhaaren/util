import gc
import sys


def _get_all_refs(ref_fn, objs, filter_fn=None, ignore_ids=frozenset(), max_depth=None, max_count=None):
    assert max_depth is None or max_depth >= 0
    assert max_count is None or max_count >= 0
    refs = []
    current_generation = {id(obj): obj for obj in objs}.values()
    current_depth = 0
    ignore_ids = set(ignore_ids) | {id(refs), id(current_generation), id(_get_all_refs)}

    def caching_predicate_(obj_):
        if id(obj_) in ignore_ids:
            return False
        if filter_fn is None:
            return True

        if filter_fn(obj_):
            return True
        ignore_ids.add(id(obj_))
        return False

    ignore_ids.add(id(caching_predicate_))

    while (not (max_depth is not None and current_depth == max_depth) and
           not (max_count is not None and len(refs) + len(current_generation) >= max_count) and
           current_generation):
        refs += current_generation
        ignore_ids |= set(map(id, current_generation))
        current_generation = filter(caching_predicate_, ref_fn(current_generation))
        current_depth += 1

    if max_count is not None and len(refs) + len(current_generation) > max_count:
        return refs
    refs += current_generation
    return refs


def get_all_referents(objs, filter_fn=None, ignore_ids=frozenset(), max_depth=None, max_count=None):
    return _get_all_refs(lambda objs_: gc.get_referents(*objs_), objs, filter_fn, ignore_ids, max_depth, max_count)


def get_all_referrers(objs, filter_fn=None, ignore_ids=frozenset(), max_depth=None, max_count=None):
    return _get_all_refs(lambda objs_: gc.get_referrers(*objs_), objs, filter_fn, ignore_ids, max_depth, max_count)


def get_total_referred_size(objs):
    return sum(map(sys.getsizeof, get_all_referents(objs)))
