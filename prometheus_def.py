import tempfile
import os
tempdir = tempfile.mkdtemp()
os.environ['prometheus_multiproc_dir'] = tempdir
import prometheus_client
from prometheus_client import multiprocess, start_http_server, Summary, Counter, Histogram, Gauge
multiprocess.MultiProcessCollector(prometheus_client.core.REGISTRY, tempdir)

RETURN_EMPTY_COUNT  = Counter('return_empty_count', 'return empty count', registry=None)
RETRIEVE_LATENCY = Histogram('retrieve_latency', 'retrieve latency', registry=None)
FAIL_COUNT  = Counter('fail_count', 'fail count', registry=None)
