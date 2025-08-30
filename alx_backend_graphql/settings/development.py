"""
Development-specific Django settings for ALX Backend GraphQL CRM project.
"""

from .base import *

# Development-specific overrides
DEBUG = True

# Add development-specific apps if needed
# INSTALLED_APPS += ['debug_toolbar']

# Development-specific middleware
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Development database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'development.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'crm': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
