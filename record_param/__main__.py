from __future__ import print_function
from util.record_param import activate

import os
import sys

# cf. profile source code

activate()

del sys.argv[0]

if not sys.argv:
    print('record_param requires a script to run', file=sys.stderr)
    sys.exit(2)

script_path = sys.argv[0]
sys.path.insert(0, os.path.dirname(script_path))
with open(script_path, 'rb') as script_file:
    script_compiled = compile(script_file.read(), script_path, 'exec', dont_inherit=1)
    script_globals = {
        '__file__': script_path,
        '__name__': '__main__',
        '__package__': None,
    }
    script_globals.update(globals())
    exec script_compiled in script_globals, None
