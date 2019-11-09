import inspect
from itertools import chain


def flatten(obj):
    if not isinstance(obj, list):
        return list(obj)

    obj = map(flatten, obj)
    ret = []
    for el in obj:
        if isinstance(el, list):
            ret.extend(el)
        else:
            ret.append(el)
    return ret


def search_fn_object(fn_name, fn_frame, calling_frame):
    fn_locals = fn_frame.f_locals
    calling_locals = calling_frame.f_locals
    calling_globals = calling_frame.f_globals

    if fn_name in calling_locals:
        return calling_locals[fn_name]

    if fn_name in calling_globals:
        return calling_globals[fn_name]

    if fn_name == '<genexpr>':
        for identifier, obj in chain(calling_locals.iteritems(), calling_globals.iteritems()):
            if hasattr(obj, 'gi_frame') and getattr(obj, 'gi_frame') is fn_frame:
                return obj

    if fn_name == '<lambda>':
        weak_match = None
        strong_match = None
        for identifier, obj in chain(calling_locals.iteritems(), calling_globals.iteritems()):
            if not (inspect.isfunction(obj) and '<lambda>' in str(obj)):
                continue

            if weak_match is None:
                weak_match = obj
            else:
                weak_match = 'multiple'

            if obj.__closure__ is None:
                continue

            argnames = set(flatten(inspect.getargspec(obj)[0]))
            local_ids = {id(v) for k, v in fn_locals.iteritems() if k not in argnames}
            calling_ids = set(map(id, calling_locals.itervalues()))

            if {id(cell.cell_contents) for cell in obj.__closure__} <= local_ids & calling_ids:
                if strong_match is None:
                    strong_match = obj
                else:
                    strong_match = 'multiple'

        if strong_match == 'multiple':
            return None
        if strong_match is not None:
            return strong_match

        return weak_match if weak_match != 'multiple' else None

    for identifier, obj in chain(calling_locals.iteritems(), calling_globals.iteritems()):
        if not hasattr(obj, fn_name) or not inspect.ismethod(getattr(obj, fn_name)):
            continue

        obj_fn = getattr(obj, fn_name)
        first_arg = inspect.getargspec(obj_fn)[0][0]
        if first_arg in fn_locals and fn_locals[first_arg] is obj:
            return obj_fn

    return None
