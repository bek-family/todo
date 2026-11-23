"""The tasks kept in the app's storage, under one key, as the phone keeps
an app's storage between its runs."""

from componentize_py_types import Err
from wit_world.imports import host_api

from tasks import Tasks

KEY = "tasks"


def load() -> Tasks:
    return Tasks.decode(host_api.storage_get(KEY))


def save(tasks: Tasks) -> bool:
    """The tasks kept; whether they could be (the storage may be full)."""
    try:
        host_api.storage_set(KEY, tasks.encode())
    except Err:
        return False
    return True
