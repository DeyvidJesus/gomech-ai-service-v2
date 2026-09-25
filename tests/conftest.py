import os

# The service assumes a deployed environment unless told otherwise, and refuses the public
# development secret there. Tests run as "test" so the app can be imported with its defaults.
os.environ.setdefault("ENVIRONMENT", "test")
