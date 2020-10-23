import logging
import multiprocessing
import time
import traceback


class TimeoutError(Exception):
    pass


class SubprocessError(Exception):
    pass


class UpdateMsg(object):
    def __init__(self, update):
        self.update = update


class ErrorMsg(object):
    def __init__(self, stack_trace):
        self.stack_trace = stack_trace


class Source(object):
    def __init__(self, target):
        self._target = target
        self._result = {}
        self._available_keys = set()
        self._done = False

        parent_conn, child_conn = multiprocessing.Pipe()
        self._conn = parent_conn
        self._proc = multiprocessing.Process(target=self._target, args=(child_conn,))
        self._proc.start()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._proc.terminate()

    def _await_and_apply(self, deadline=None):
        if self._done:  # assert?
            return

        try:
            if deadline is None:
                msg = self._conn.recv()
            else:
                if not self._conn.poll(max(deadline - time.time(), 0)):
                    raise TimeoutError('Waiting on message from subprocess')
                msg = self._conn.recv()
        except EOFError:
            self._done = True
            return
        if isinstance(msg, ErrorMsg):
            logging.error('Received exception from subprocess: {}'.format(msg.stack_trace))
            self.close()
            raise SubprocessError()
        new_keys = set(msg.update)
        if any(k in self._result for k in new_keys):
            logging.error('Subprocess produced duplicate keys')
            self.close()
            raise SubprocessError()
        self._result.update(msg.update)
        self._available_keys.update(new_keys)
        return new_keys

    def await_result(self, timeout_s=None):
        deadline = None
        if timeout_s is not None:
            deadline = time.time() + timeout_s
        while not self._done:
            self._await_and_apply(deadline)
        return self._result

    def await_key(self, key, timeout_s=None):
        deadline = None
        if timeout_s is not None:
            deadline = time.time() + timeout_s
        while not self._done and key not in self._result:
            self._await_and_apply(deadline)
        # If not in there then we must be done and it is missing
        self._available_keys.discard(key)
        return self._result[key]

    # Returns a key and value not seen before, StopIteration if there are none and we are done
    def await_any(self, timeout_s=None):
        deadline = None
        if timeout_s is not None:
            deadline = time.time() + timeout_s
        while not self._done and not self._available_keys:
            self._await_and_apply(deadline)

        if not self._available_keys:
            # Must be done
            raise StopIteration()
        key = self._available_keys.pop()
        return key, self._result[key]

    def __iter__(self):
        return self

    def next(self):
        return self.await_any()

    # Allow for timeouts between results while iterating over not seen before
    def iter(self, timeout_s=None):
        while True:
            try:
                yield self.await_any(timeout_s)
            except StopIteration:
                break

    # Returns a key and value not seen before matching the filter, StopIteration if there are none and we are done
    # Maybe more/different timeout options here?
    def await_any_matching(self, filter_fn, timeout_s=None, available_matching=None, unknown=None):
        available_matching = set() if available_matching is None else available_matching
        unknown = self._available_keys - available_matching if unknown is None else unknown

        def classify_unknown_():
            for k in unknown:
                if filter_fn(k, self._result[k]):
                    available_matching.add(k)
            unknown.clear()

        classify_unknown_()

        deadline = None
        if timeout_s is not None:
            deadline = time.time() + timeout_s

        while not self._done and not available_matching:
            unknown.update(self._await_and_apply(deadline))
            classify_unknown_()

        if not available_matching:
            # Must be done
            raise StopIteration()
        key = available_matching.pop()
        return key, self._result[key]

    # An iterator over not seen before with filtering pre-applied and a timeout option
    def iter_matching(self, filter_fn, timeout_s=None):
        available_matching = {k for k in self._available_keys if filter_fn(k, self._result[k])}
        unknown = set()
        while True:
            try:
                yield self.await_any_matching(filter_fn, timeout_s, available_matching, unknown)
            except StopIteration:
                break


def source_from_function(f, *args, **kwargs):
    def target_(child_conn):
        try:
            result = f(*args, **kwargs)
            child_conn.send(UpdateMsg(result))
            child_conn.close()
        except Exception:
            child_conn.send(ErrorMsg(traceback.format_exc()))
            raise

    return Source(target_)


def source_from_generator_function(g, *args, **kwargs):
    def target_(child_conn):
        try:
            for result in g(*args, **kwargs):
                child_conn.send(UpdateMsg(result))
            child_conn.close()
        except Exception:
            child_conn.send(ErrorMsg(traceback.format_exc()))
            raise

    return Source(target_)
