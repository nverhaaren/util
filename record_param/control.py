_active = False


def activate():
    global _active
    _active = True


def is_active():
    return _active
