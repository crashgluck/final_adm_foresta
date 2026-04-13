from __future__ import annotations

from threading import local

_thread_local = local()


def set_current_user(user):
    _thread_local.user = user


def get_current_user():
    return getattr(_thread_local, 'user', None)

