import os
from distutils.util import strtobool

EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_USE_TLS = strtobool(os.environ.get("EMAIL_USE_TLS"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
