# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "talentofutpay"

# Server mechanics
daemon = False
pidfile = "talentofutpay.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (si se usa directamente con Gunicorn)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
