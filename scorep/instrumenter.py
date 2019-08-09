import scorep.instrumenters.dummy

global_instrumenter = None


def get_instrumenter(
        bindings=None,
        enable_instrumenter=False,
        instrumenter_type="dummy"):
    """
    returns an instrumenter

    @param bindings the c/c++ scorep bindings
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

    def __init__(self):
        pass

    def __enter__(self):
        self.tracer_registered = get_instrumenter().register()

    def __exit__(self, exc_type, exc_value, traceback):
        self.tracer_registered = get_instrumenter().unregister()


class disable():
    """
    Context manager to disable tracing in a certain region:
    ```
    with disable():
        do stuff
    ```
    This overides --no-instrumenter (--nopython leagacy)
    """

    def __init__(self):
        pass

    def __enter__(self):
        self.tracer_registered = get_instrumenter().unregister()

    def __exit__(self, exc_type, exc_value, traceback):
        self.tracer_registered = get_instrumenter().register()
