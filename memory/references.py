import gc
import sys


class SearchLimitException(Exception):
    pass


def _get_all_refs(ref_fn, objs, allowed_ids, filter_fn=lambda _: True, max_depth=None, max_count=None,
                  allow_partial=True):
    assert max_depth is None or max_depth >= 0
    assert max_count is None or max_count >= 0
    refs = []
    current_generation = {id(obj): obj for obj in objs}.values()
    current_depth = 0
    allowed_ids = set(allowed_ids)
    allowed_ids.discard(id(_get_all_refs))

    def caching_predicate_(obj_):
        if id(obj_) not in allowed_ids:
            return False

        if filter_fn(obj_):
            return True
        allowed_ids.discard(id(obj_))
        return False

    while (not (max_depth is not None and current_depth == max_depth) and
           not (max_count is not None and len(refs) + len(current_generation) >= max_count) and
           current_generation):
        refs.extend(current_generation)
        allowed_ids -= set(map(id, current_generation))
        current_generation = filter(caching_predicate_, ref_fn(current_generation))
        current_depth += 1

    if not allow_partial and current_generation:
        raise SearchLimitException()

    if max_count is not None and len(refs) + len(current_generation) > max_count:
        return refs
    refs += current_generation
    return refs


def get_all_referents(objs, filter_fn=lambda _: True, ignore_ids=frozenset(), max_depth=None, max_count=None,
                      allow_partial=True):
    allowed_ids = set(map(id, gc.get_objects()))
    allowed_ids -= ignore_ids
    return _get_all_refs(lambda objs_: gc.get_referents(*objs_), objs, allowed_ids, filter_fn, max_depth, max_count,
                         allow_partial)


def get_all_referrers(objs, filter_fn=lambda _: True, ignore_ids=frozenset(), max_depth=None, max_count=None,
                      allow_partial=True):
    allowed_ids = set(map(id, gc.get_objects()))
    allowed_ids.discard(id(get_all_referrers))
    allowed_ids.discard(id(locals()))
    allowed_ids.discard(id(objs))
    allowed_ids -= ignore_ids
    return _get_all_refs(lambda objs_: gc.get_referrers(*objs_), objs, allowed_ids, filter_fn, max_depth, max_count,
                         allow_partial)


def get_proper_referents(objs, filter_fn=lambda _: True, ignore_ids=frozenset(), max_depth=None, max_count=None,
                         allow_partial=True):
    root_ids = set(map(id, objs))
    all_referents = get_all_referents(objs, filter_fn, ignore_ids, max_depth, max_count, allow_partial)
    return [obj for obj in all_referents if id(obj) not in root_ids]


def get_proper_referrers(objs, filter_fn=lambda _: True, ignore_ids=frozenset(), max_depth=None, max_count=None,
                         allow_partial=True):
    root_ids = set(map(id, objs))
    all_referrers = get_all_referrers(objs, filter_fn, ignore_ids, max_depth, max_count, allow_partial)
    return [obj for obj in all_referrers if id(obj) not in root_ids]


def get_all_dependents(objs, filter_fn=lambda _: True, ignore_ids=frozenset(), max_depth=None, max_count=None,
                       filter_referrers=lambda _: True, ignore_referrers=frozenset()):
    referents = get_proper_referents(objs, filter_fn, ignore_ids, max_depth, max_count, allow_partial=False)
    referent_ids = set(map(id, referents))

    dependents = [obj for obj in referents
                  if (set(map(id, filter(filter_referrers, gc.get_referrers(obj)))) - ignore_referrers) <= referent_ids]

    return dependents


def get_total_referred_size(objs):
    return sum(map(sys.getsizeof, get_all_referents(objs)))


def get_collection_gain(objs):
    return sum(map(sys.getsizeof, {id(obj): obj for obj in objs}.values())) + sum(map(sys.getsizeof, get_all_dependents(objs)))
