### gunicorn conf

## 
ROOT = '/var/web/orro/'

## Server Socket
bind = '127.0.0.1:5055'

backlog = 2048

## Worker Processes
workers = 1
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
timeout = 30
keepalive = 2

debug = False
spew = False

## Server Mechanics
chdir = ROOT
preload_app = True
daemon = True
pidfile = '/var/run/gunicorn.pid'
#user = 'gunicorn'
#group = 'gunicorn'
#umask = 0002

## Logging
# logfile = '/usr/local/gunicorn/logs/gunicorn.log'
accesslog = ROOT + 'logs/gunicorn_access.log'
errorlog = ROOT + 'logs/gunicorn.log'
loglevel = 'info'
#logconfig = None

## Process Naming
proc_name = 'gunicorn'
