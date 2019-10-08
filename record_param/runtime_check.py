from __future__ import absolute_import

from util.record_param.lemma import find_nested_index, at_nested_index
from .control import is_active
import inspect


_wrapper_originals = {}


def _passes(arg, attrset):
    return all(hasattr(arg, attr) for attr in attrset)


def _missing(arg, attrset):
    return {attr for attr in attrset if not hasattr(arg, attr)}


def _verify(arg, attrset, error_message_template):
    if not _passes(arg, attrset):
        raise TypeError(error_message_template.format(arg=arg, missing=', '.join(_missing(arg, attrset))))


def annotate(argname, attrset):
    if not is_active():
        return lambda fn: fn

    def functor(fn):
        effective_fn = _wrapper_originals.get(fn, fn)
        argspec = inspect.getargspec(effective_fn)

        try:
            fn_str = 'Function {} at {}:{}'.format(effective_fn.func_name, inspect.getfile(effective_fn),
                                                   inspect.getsourcelines(effective_fn)[1])
        except IOError:
            fn_str = repr(effective_fn)

        try:
            nested_idx = find_nested_index(argspec.args, argname)
        except ValueError:
            raise TypeError('{} has no argument {}'.format(fn_str, argname))

        earliest_default_index = len(argspec.args) - len(argspec.defaults or ())

        default_index = list(nested_idx)
        default_index[0] -= earliest_default_index

        if default_index >= 0:
            _verify(at_nested_index(argspec.defaults, default_index), attrset,
                    '{fn}: default value for {argname} ({{arg}}) is missing {{missing}}'.format(
                        fn=fn_str, argname=argname))

        def wrapper(*args, **kwargs):
            error_message_template = '{fn}: {argname} ({{arg}}) is missing {{missing}}'.format(
                fn=fn_str, argname=argname)
            if len(args) > nested_idx[0]:
                _verify(at_nested_index(args, nested_idx), attrset, error_message_template)
            elif argname in kwargs:
                _verify(kwargs[argname], attrset, error_message_template)

            return fn(*args, **kwargs)

        _wrapper_originals[wrapper] = effective_fn

        return wrapper

    return functor
