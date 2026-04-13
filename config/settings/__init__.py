import os

env = os.getenv('DJANGO_ENV', 'local').lower()

if env == 'production':
    from .production import *  # noqa
elif env == 'test':
    from .test import *  # noqa
else:
    from .local import *  # noqa

