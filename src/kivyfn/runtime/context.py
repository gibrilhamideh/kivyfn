_current_runtime = None


def set_runtime(runtime):
    global _current_runtime
    _current_runtime = runtime


def get_runtime():
    if _current_runtime is None:
        raise RuntimeError("No runtime is active")

    return _current_runtime
