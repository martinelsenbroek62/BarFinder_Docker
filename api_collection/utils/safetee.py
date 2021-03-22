"""
shamelessly copied from: https://stackoverflow.com/a/44638570/2644759
"""
from itertools import tee
from threading import Lock


class safeteeobject(object):
    """tee object wrapped to make it thread-safe"""

    def __init__(self, teeobj, lock):
        self.teeobj = teeobj
        self.lock = lock

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            ok, payload = next(self.teeobj)
            if ok:
                return payload
            else:
                raise payload

    def __copy__(self):
        return safeteeobject(self.teeobj.__copy__(), self.lock)


def iter_with_exceptions(iterable):
    try:
        for payload in iterable:
            yield True, payload
    except Exception as exc:
        yield False, exc


def safetee(iterable, n=2):
    """tuple of n independent thread-safe iterators"""
    lock = Lock()
    iterable = iter_with_exceptions(iterable)
    return tuple(safeteeobject(teeobj, lock) for teeobj in tee(iterable, n))
