import os

bind = "0.0.0.0:8000"
workers = 1
accesslog = "logs/gunicorn.access.log"
errorlog = "logs/gunicorn.error.log"
capture_output = True
loglevel = os.getenv('LOG_LEVEL', default='info').lower()
