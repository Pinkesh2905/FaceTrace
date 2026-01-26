import multiprocessing

# Bind to all interfaces on port 8000
bind = "0.0.0.0:8000"

# Worker Configuration
# Face recognition is CPU bound. Don't spawn too many workers or they will fight for CPU.
# Formula: (2 x num_cores) + 1 usually, but for heavy ML tasks, 1 worker per core is safer.
workers = multiprocessing.cpu_count() 

# Use threads for handling concurrent requests within a worker
threads = 2

# Timeout configuration
# ML tasks might take longer than standard requests
timeout = 120 
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process Naming
proc_name = "face_cognition_app"