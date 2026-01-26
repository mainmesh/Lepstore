from lepstore.wsgi import application

# Expose WSGI application for hosting platforms or adapters that look for
# a top-level `app` or `application` symbol.
app = application
