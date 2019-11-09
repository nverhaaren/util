import inspect
import unittest

from util.stack_fn import search_fn_object


def module_fn():
    stack = inspect.stack()
    fn_name = stack[0][3]
    local_frame = stack[0][0]
    calling_frame = stack[1][0]

    return search_fn_object(fn_name, local_frame, calling_frame)


def module_gen():
    stack = inspect.stack()
    fn_name = stack[0][3]
    local_frame = stack[0][0]
    calling_frame = stack[1][0]

    yield search_fn_object(fn_name, local_frame, calling_frame)


class X(object):
    def instance_method(self):
        stack = inspect.stack()
        fn_name = stack[0][3]
        local_frame = stack[0][0]
        calling_frame = stack[1][0]

        return search_fn_object(fn_name, local_frame, calling_frame)

    @classmethod
    def class_method(cls):
        stack = inspect.stack()
        fn_name = stack[0][3]
        local_frame = stack[0][0]
        calling_frame = stack[1][0]

        return search_fn_object(fn_name, local_frame, calling_frame)


class TestSearchFnObject(unittest.TestCase):
    def test_basic(self):
        def local_fn():
            stack = inspect.stack()
            fn_name = stack[0][3]
            local_frame = stack[0][0]
            calling_frame = stack[1][0]

            return search_fn_object(fn_name, local_frame, calling_frame)

        self.assertIs(local_fn(), local_fn)

        self.assertIs(module_fn(), module_fn)

        x = X()
        self.assertEqual(x.instance_method(), x.instance_method)

        self.assertEqual(X.class_method(), X.class_method)

        lam = lambda: inspect.stack()
        lam_stack = lam()
        fn_name = lam_stack[0][3]
        local_frame = lam_stack[0][0]
        calling_frame = lam_stack[1][0]

        self.assertIs(search_fn_object(fn_name, local_frame, calling_frame), lam)

        def local_gen():
            stack = inspect.stack()
            fn_name = stack[0][3]
            local_frame = stack[0][0]
            calling_frame = stack[1][0]

            yield search_fn_object(fn_name, local_frame, calling_frame)

        self.assertIs(next(local_gen()), local_gen)

        self.assertIs(next(module_gen()), module_gen)

        gen = (inspect.stack() for _ in range(1))
        gen_stack = next(gen)
        fn_name = gen_stack[0][3]
        local_frame = gen_stack[0][0]
        calling_frame = gen_stack[1][0]

        self.assertIs(search_fn_object(fn_name, local_frame, calling_frame), gen)
