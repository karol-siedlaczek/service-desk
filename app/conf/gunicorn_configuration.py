import os

bind = "0.0.0.0:8000"
workers = int(os.getenv('GUNICORN_WORKERS', default='1'))
accesslog = "logs/gunicorn.access.log"
errorlog = "logs/gunicorn.error.log"
capture_output = True
loglevel = os.getenv('LOG_LEVEL', default='info').lower()


# Prometheus multiprocess support.
# With more than one worker each process keeps its own in-memory metrics, so a
# scrape would only ever see one worker. prometheus_client solves this by having
# every worker write to files under PROMETHEUS_MULTIPROC_DIR; django_prometheus'
# export view then aggregates them. The directory must exist and be emptied at
# startup (stale .db files from a previous run would inflate counters), and dead
# workers must be reaped so their series stop being exported.
# Everything below is a no-op unless PROMETHEUS_MULTIPROC_DIR is set.
def on_starting(server):
    prom_dir = os.getenv('PROMETHEUS_MULTIPROC_DIR')
    if not prom_dir:
        return
    os.makedirs(prom_dir, exist_ok=True)
    for entry in os.listdir(prom_dir):
        if entry.endswith('.db'):
            os.remove(os.path.join(prom_dir, entry))


def child_exit(server, worker):
    if not os.getenv('PROMETHEUS_MULTIPROC_DIR'):
        return
    from prometheus_client import multiprocess
    multiprocess.mark_process_dead(worker.pid)
