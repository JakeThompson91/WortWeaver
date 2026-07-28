# Gunicorn Production Configuration for WortWeaver

import multiprocessing

# Server Socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker Processes & Concurrency
# Uses gthread worker class with 2 threads per process for concurrent translation handling
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
worker_class = "gthread"
threads = 2

# Worker Timeout
# Set to 120 seconds to accommodate large document translation tasks without process termination
timeout = 120
keepalive = 5

# Logging
loglevel = "info"
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr

# Process Name
proc_name = "wortweaver_gunicorn"

# Worker Memory Leak Protection & Recycling
max_requests = 1000
max_requests_jitter = 50
