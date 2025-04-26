import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = 'asset_tracker'

# Logging
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'

# SSL
keyfile = os.getenv('SSL_KEY_PATH')
certfile = os.getenv('SSL_CERT_PATH')

# Process management
daemon = False
pidfile = '/var/run/gunicorn.pid'
umask = 0o027
user = None
group = None
tmp_upload_dir = None

# Server mechanics
preload_app = True
reload = False
reload_engine = 'auto'
spew = False
check_config = False

# Server hooks
def on_starting(server):
    pass

def on_reload(server):
    pass

def when_ready(server):
    pass

def on_exit(server):
    pass

# Django WSGI application path
wsgi_app = "asset_tracker.wsgi:application"