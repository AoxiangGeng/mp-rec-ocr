import os, socket, sys, time, errno, random
from pytools.program.fmtutil import fmt_exception
from thrift.transport.TTransport import TTransportException
from thrift.transport.TSocket import TSocket
from thrift.Thrift import TException

class TSocketPool(TSocket):
    '''
    TSocketPool([('192.168.10.85', 8090), ('192.168.10.87', 9090)])
    or TSocketPool('192.168.10.86', 8754)
    '''

    serverStates = {}

    def __init__(self, host, port=None, timeout=None, conn_timeout=None, randomizer=None, use_translate=False):
        TSocket.__init__(self)
        self.timeout = timeout
        self.conn_timeout = conn_timeout if conn_timeout else timeout
        self.servers = []
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

        if type(port) is list:
            port = [p for p in port if p]
            for i in range(0, len(port)):
                self.servers.append((host[i], int(port[i])))
        elif type(host) is list:
            host = [h for h in host if h]
            self.servers = host
        else:
            self.servers = [(host, int(port))]
        if use_translate:
            from pyutil.consul.bridge import translate
            self.servers = translate(self.servers)

    def open(self):
        # Check if we want order randomization
        servers = self.servers
        if self.randomize:
            servers = []
            oldServers = []
            oldServers.extend(self.servers)
            while len(oldServers):
                pos = int(self.random.random() * len(oldServers))
                servers.append(oldServers[pos])
                oldServers[pos] = oldServers[-1]
                oldServers.pop()

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
                        # Successful connection, return now
                        return
                    except TTransportException as e:
                        # Connection failed
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

        # Oh no; we failed them all. The system is totally ill!
        hostlist = ','.join(['%s:%d' % (s[0], s[1]) for s in self.servers])
        error = 'All hosts in pool are down (%s). Last Exception: %s.' % (hostlist,
                fmt_exception(self.last_err) if self.last_err else '')

        raise TException(error)
