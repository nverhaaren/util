import sys
from util.record_param import annotate


class X(object):
    x = 0


@annotate('x', {'x'})
def f(x):
    print x
    print sys.argv


f(X())
f(0)
