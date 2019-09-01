from __future__ import absolute_import
from .control import is_active
import inspect


def _passes(arg, attrset):
    return all(hasattr(arg, attr) for attr in attrset)


def _missing(arg, attrset):
    return {attr for attr in attrset if not hasattr(arg, attr)}


def _verify(arg, attrset, fn_str, argname):
    if not _passes(arg, attrset):
        raise TypeError('{}: default value for {} ({}) is missing {}'.format(
            fn_str, argname, arg, ', '.join(_missing(arg, attrset))))


def annotate(argname, attrset):
    if not is_active():
        return lambda fn: fn

    def functor(fn):
        argspec = inspect.getargspec(fn)

        try:
            fn_str = 'Function {} at {}:{}'.format(fn.func_name, inspect.getfile(fn), inspect.getsourcelines(fn)[1])
        except IOError:
            fn_str = repr(fn)

        try:
            # TODO: currently only handles non-nested arg lists
            index = argspec.args.index(argname)
        except ValueError:
            raise TypeError('{} has no argument {}'.format(fn_str, argname))

        earliest_default_index = len(argspec.args) - len(argspec.args or ())

        default_index = index - earliest_default_index

        if default_index >= 0:
            _verify(argspec.defaults[default_index], attrset, fn_str, argname)

        def wrapper(*args, **kwargs):
            if len(args) > index:
                _verify(args[index], attrset, fn_str, argname)
            elif argname in kwargs:
                _verify(kwargs[argname], attrset, fn_str, argname)

            return fn(*args, **kwargs)

        return wrapper

    return functor

