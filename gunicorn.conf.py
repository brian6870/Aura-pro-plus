#!/usr/bin/env python3
"""
Gunicorn configuration for Aura Carbon Tracker
Production-only configuration
"""
import os
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

# Security - critical for production
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "aura_app"

# Server mechanics
daemon = False
pidfile = "/tmp/aura.pid"
umask = 0
user = "www-data"
group = "www-data"

# Logging - extensive in production
accesslog = "/var/log/aura/access.log"
errorlog = "/var/log/aura/error.log"
loglevel = "warning"

# Log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process management
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Environment
raw_env = [
    'FLASK_ENV=production'
]