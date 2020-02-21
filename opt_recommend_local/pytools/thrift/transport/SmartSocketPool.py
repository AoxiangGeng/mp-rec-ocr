import os, socket, sys, time, errno, random
from pyutil.program.fmtutil import fmt_exception
from thrift.transport.TTransport import TTransportException
from thrift.transport.TSocket import TSocket
from thrift.Thrift import TException
import pyutil.program.metrics2 as metrics

from pyutil.consul.bridge import translate_one
from pyutil.consul.watch import add_watch
from pyutil.consul.watch import remove_watch
import threading, logging

class TSocketPool(TSocket):
    '''
    Enable socketpool to use latest hosts list in consul.

    TODO(mengweichao): Get hosts list by using corresponding meta info which `identity:service_name` denotes.
    '''

    serverStates = {}

    def __init__(self, service_name, identity,timeout=None, conn_timeout=None, randomizer=None, max_total_timeout=None):
        TSocket.__init__(self)
        self.timeout = timeout
        self.conn_timeout = conn_timeout if conn_timeout else timeout
        self.randomize = True
        if randomizer:
            self.random = randomizer
        else:
            self.random = random
        self.retryInterval = 5
        self.numRetries = 1
        self.maxConsecutiveFailures = 2
        self.alwaysTryLast = False
        self.last_err = ''
        self.lock = threading.Lock()
        self.service_name = service_name
        self.servers = []
        self.identity= identity
        self.last_watch_change_time = time.time()
        self.max_total_timeout = max_total_timeout if max_total_timeout else 0.2
        self.total_retry_num = 0
        self._define_metrics()
        self.tags = {'identity': self.identity, 'servicename': self.service_name }
        self.update_servers()

    def _define_metrics(self):
        metrics.define_tagkv('identity', [self.identity])
        metrics.define_tagkv('servicename', [self.service_name])
        metrics.define_counter("smart.socketpool.retry_num","num", prefix="inf")
        metrics.define_timer("smart.socketpool.open_time","ms", prefix="inf")
        metrics.define_counter("smart.socketpool.connect_fail","num", prefix="inf")
        metrics.define_counter("smart.socketpool.acquire_fail","num", prefix="inf")
        metrics.define_timer("smart.socketpool.nodeschange.interval", "ms", prefix="inf")
        metrics.define_store("smart.socketpool.nodeschange.num", "num", prefix="inf")
        metrics.define_timer("smart.socketpool.nodesnum", "num", prefix="inf")

    def update_servers(self):
        server_list = translate_one(self.service_name)
        if not isinstance(server_list[0], tuple):
            metrics.emit_counter("smart.socketpool.acquire_fail", 1, prefix="inf", tagkv=self.tags)
            time.sleep(10)
            raise TException("no hosts registered on %s " % self.service_name)
        self.lock.acquire(True)
        self.servers = server_list
        self.lock.release()
        def server_change_callback(name, nodes):
            logging.debug("the service name %s, %s  hosts %s ", name,len(nodes), nodes)
            # incase metrics.emit block other threads acquire the lock, we just
            # simplify the logic by moving emit out of the critical section
            old_time = None
            new_time = None
            is_abnormal_nodes = False
            self.lock.acquire(True)
            old_time = self.last_watch_change_time
            self.last_watch_change_time = time.time()
            new_time = self.last_watch_change_time
            if len(nodes) == 0:
                # we still use old nodes list
                is_abnormal_nodes = True
            elif len(nodes)  * 2 + 1 < len(self.servers): # in case the server drastically down
                is_abnormal_nodes =  True
            else:
                self.servers = nodes
            self.lock.release()
            if is_abnormal_nodes:
                metrics.emit_counter("smart.socketpool.acquire_fail", 1, prefix="inf",tagkv=self.tags)
            metrics.emit_timer("smart.socketpool.nodeschange.interval", (new_time - old_time)* 1000000, prefix="inf",tagkv=self.tags)
            metrics.emit_store("smart.socketpool.nodeschange.num", len(nodes), prefix="inf",tagkv=self.tags)
        self.watch_id = add_watch(self.service_name, server_change_callback)
    
    def __del__(self):
        remove_watch(self.service_name, self.watch_id)

    def open(self):
        self.lock.acquire(True)
        metrics.emit_timer("smart.socketpool.nodesnum",len(self.servers), prefix="inf", tagkv=self.tags)
        # Check if we want order randomization
        ts = time.time()
        servers = self.servers
        self.lock.release()
        if self.randomize:
            random.shuffle(servers)
        start_time = time.time()
        self.total_retry_num = 0
        # Count servers to identify the "last" one
        for i in range(0, len(servers)):
            # This extracts the $host and $port variables
            host, port = servers[i]
            # Check APC cache for a record of this server being down
            failtimeKey = 'thrift_failtime:%s%d~' % (host, port)
            # Cache miss? Assume it's OK
            lastFailtime = TSocketPool.serverStates.get(failtimeKey, 0)
            retryIntervalPassed = False
            # Cache hit...make sure enough the retry interval has elapsed
            if lastFailtime > 0:
                elapsed = int(time.time()) - lastFailtime
                if elapsed > self.retryInterval:
                    retryIntervalPassed = True

            # Only connect if not in the middle of a fail interval, OR if this
            # is the LAST server we are trying, just hammer away on it
            isLastServer = self.alwaysTryLast and i == (len(servers) - 1) or False

            if lastFailtime == 0 or isLastServer or (lastFailtime > 0 and retryIntervalPassed):
                # Set underlying TSocket params to this one
                self.host = host
                self.port = port
                # Try up to numRetries_ connections per server
                for attempt in range(0, self.numRetries):
                    try:
                        # Use the underlying TSocket open function
                        if self.conn_timeout:
                            self.setTimeout(self.conn_timeout * 1000)
                        TSocket.open(self)
                        if self.timeout:
                            self.setTimeout(self.timeout * 1000)
                        # Only clear the failure counts if required to do so
                        if lastFailtime > 0:
                            TSocketPool.serverStates[failtimeKey] = 0

                        metrics.emit_counter("smart.socketpool.retry_num",self.total_retry_num, prefix="inf",tagkv=self.tags)
                        metrics.emit_timer("smart.socketpool.open_time", (time.time() - ts)*1000000, prefix='inf',tagkv=self.tags)
                        # Successful connection, return now
                        return
                    except TTransportException as e:
                        # Connection failed
                        metrics.emit_counter("smart.socketpool.connect_fail", 1, prefix="inf",tagkv=self.tags)
                        self.last_err = e
                    except Exception as e:
                        self.last_err = e
                # Mark failure of this host in the cache
                consecfailsKey = 'thrift_consecfails:%s%d~' % (host, port)
                # Ignore cache misses
                consecfails = TSocketPool.serverStates.get(consecfailsKey, 0)

                # Increment by one
                consecfails += 1
                # Log and cache this failure
                if consecfails >= self.maxConsecutiveFailures:
                    # Store the failure time
                    TSocketPool.serverStates[failtimeKey] =  int(time.time())
                    # Clear the count of consecutive failures
                    TSocketPool.serverStates[consecfailsKey] = 0
                else:
                    TSocketPool.serverStates[consecfailsKey] = consecfails
                self.total_retry_num += 1
                logging.warn("retry connect : %d, last failed host : %s, time used:%f"%(self.total_retry_num, str(servers[i]),time.time() - start_time))
                if time.time() - start_time > self.max_total_timeout:
                    error = 'max_total_time(%f) is up, total_retry_num : %d. last failed host : %s, Last Exception: %s.' % (self.max_total_timeout, self.total_retry_num, str(servers[i]), fmt_exception(self.last_err) if self.last_err else '')
                    metrics.emit_timer("smart.socketpool.open_time", (time.time() - ts)*1000000, prefix='inf',tagkv=self.tags)
                    metrics.emit_counter("smart.socketpool.retry_num",self.total_retry_num, prefix="inf",tagkv=self.tags)
                    raise TException(error)
        metrics.emit_timer("smart.socketpool.open_time", (time.time() - ts)*1000000, prefix='inf',tagkv=self.tags)
        metrics.emit_counter("smart.socketpool.retry_num",self.total_retry_num, prefix="inf",tagkv=self.tags)
        # Oh no; we failed them all. The system is totally ill!
        hostlist = ','.join(['%s:%d' % (s[0], s[1]) for s in self.servers])
        error = 'All hosts in pool are down (%s). Last Exception: %s.' % (hostlist,
                fmt_exception(self.last_err) if self.last_err else '')
        raise TException(error)
