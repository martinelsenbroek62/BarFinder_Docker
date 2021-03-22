"""Iter function with timeout parameter"""
import ctypes
from functools import wraps
from threading import Thread
from queue import Queue, Empty

from flask import current_app as app

STOP_ITERATION = object()


def put_queue(callback, queue, args, kwargs):
    from .. import app
    try:
        with app.app_context():
            iterable = callback(*args, **kwargs)
            for item in iterable:
                queue.put((True, item))
            queue.put((True, STOP_ITERATION))
    except (KeyboardInterrupt, SystemExit) as exc:
        raise exc
    except Exception as exc:
        queue.put((False, str(exc)))


def interrupt_thread(thread, exc_class=SystemExit):
    tid = thread.ident
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_ulong(tid), ctypes.py_object(exc_class))

    if res == 0:
        # thread already exit, no need to do anything
        pass
    if res != 1:
        # something wrong, set exc_class to None to revert the effect
        ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_ulong(tid), None)
        raise SystemError('PyThreadState_SetAsyncExc failed')


def iter_with_timeout(timeout=app.config['DEFAULT_ITERATION_TIMEOUT']):
    def decorator(callback):

        @wraps(callback)
        def wrapper(*args, **kwargs):
            queue = Queue()
            thread = Thread(
                target=put_queue,
                args=(callback, queue,
                      args, kwargs),
                daemon=True
            )
            thread.start()
            while True:
                try:
                    ok, payload = queue.get(timeout=timeout)
                    if not ok:
                        raise RuntimeError(payload)
                except Empty:
                    interrupt_thread(thread)
                    raise TimeoutError(
                        'An iteration in function {} exceeded the '
                        'maximum allowable time ({}s)'
                            .format(callback.__name__, timeout)
                    )
                if payload == STOP_ITERATION:
                    break
                yield payload

        return wrapper

    return decorator
