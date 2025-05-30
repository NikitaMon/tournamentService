import multiprocessing

bind = "unix:/run/gunicorn.sock"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = "tournament_gunicorn"

# SSL
keyfile = "/var/www/tournament/ssl/mytournament.ru.key"
certfile = "/var/www/tournament/ssl/mytournament.ru.full.crt" 