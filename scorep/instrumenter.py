import scorep.instrumenters.dummy
import platform

global_instrumenter = None


def has_c_instrumenter():
    """Return true if the C instrumenter(s) are available"""
    # We are using the UTF-8 string features from Python 3
    # The C Instrumenter functions are not available on PyPy
    return platform.python_implementation() != 'PyPy'


def get_instrumenter(
        enable_instrumenter=False,
        instrumenter_type="dummy"):
    """
    returns an instrumenter

    @param enable_instrumenter True if the Instrumenter should be enabled when run is called
    @param instrumenter_type which python tracing interface to use. Currently available: `profile` (default), `trace` and `dummy`
    """
    global global_instrumenter
    if global_instrumenter is None:
        global_instrumenter = scorep.instrumenters.dummy.ScorepDummy(
            enable_instrumenter)

    return global_instrumenter


def register():
    """
    Reenables the python-tracing.
    """
    get_instrumenter().register()


def unregister():
    """
    Disables the python-tracing.
    Disabling the python-tracing is more efficient than disable_recording, as python does not longer call the tracing module.
    However, all the other things that are traced by Score-P will still be recorded.
    Please call register() to enable tracing again.
    """
    get_instrumenter().unregister()


class enable():
    """
    Context manager to enable tracing in a certain region:
    ```
    with enable():
        do stuff
    ```
    This overides --no-instrumenter (--nopython leagacy)
    """

    def __init__(self, region_name=""):
        pass

    def __enter__(self):
        self.tracer_registered = scorep.instrumenter.get_instrumenter().get_registered()
        if not self.tracer_registered:
            scorep.instrumenter.get_instrumenter().register()

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.tracer_registered:
            scorep.instrumenter.get_instrumenter().unregister()

    def _recreate_cm(self):
        return self

    def __call__(self, func):
        with disable():
            @functools.wraps(func)
            def inner(*args, **kwds):
                with self._recreate_cm():
                    return func(*args, **kwds)
        return inner

class disable():
    """
    Context manager to disable tracing in a certain region:
    ```
    with disable():
        do stuff
    ```
    This overides --no-instrumenter (--nopython leagacy)
    """

    def __init__(self, region_name=""):
        pass

    def __enter__(self):
        self.tracer_registered = scorep.instrumenter.get_instrumenter().get_registered()
        if self.tracer_registered:
            scorep.instrumenter.get_instrumenter().unregister()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.tracer_registered:
            scorep.instrumenter.get_instrumenter().register()

    def _recreate_cm(self):
        return self

    def __call__(self, func):
        self.__enter__()
        try:
            @functools.wraps(func)
            def inner(*args, **kwds):
                with self._recreate_cm():
                    return func(*args, **kwds)
        finally:
            self.__exit__()
        return inner
