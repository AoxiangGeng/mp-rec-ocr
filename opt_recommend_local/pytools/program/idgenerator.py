'''
To see supported namespaces and countspaces, visit http://10.4.26.106:9500/reload
'''
import logging
import random
import threading
from conf2 import Conf
from urllib3 import connection_from_url, Timeout

logger = logging.getLogger("idgenerator")
rand = random.SystemRandom()

TIMEOUT = 4
CLUSTERS = {
    "TIANJIN": ["http://10.4.26.106:8082/", "http://10.4.16.208:8082/"],
}


class IDGeneratorClient(object):
    def __init__(self, cluster="TIANJIN", max_retries=3):
        if cluster == "AWS":
            conf = Conf('/opt/tiger/ss_conf/ss/id_generator.conf')
            self.servers = conf.id_generator_addr.split(',')
        else:
            self.servers = CLUSTERS.get(cluster)
        if not self.servers:
            raise ValueError("cluster '%s' not exists" % cluster)
        self.max_retries = max_retries
        self.lock = threading.Lock()

    def pick_conn(self, new=False):
        with self.lock:
            conn = getattr(self, "conn", None)
            if new is False and conn:
                return conn
            s = rand.choice(self.servers)
            self.conn = connection_from_url(s,
                                            maxsize=4,
                                            timeout=Timeout(TIMEOUT))
            return self.conn

    def gen_v0(self, namespace):
        """
        gen_v0 generates 52bit unique ID
        timestamp = $ID >> 20
        """
        return self.gen_multi_v0(namespace, 1)[0]

    def gen_multi_v0(self, namespace, count):
        """
        gen_multi_v0 generates count# of 52bit unique ID list
        """
        conn = self.pick_conn()
        retries = self.max_retries
        url = "/v0/gen?ns=%s&count=%d" % (namespace, count)
        while 1:
            try:
                r = conn.request("GET", url)
                content = r.data
                assert r.status == 200, "http status(%d) != 200 : %s" % (
                    r.status, content
                )
                return [int(i) for i in content.split(",")]
            except Exception as e:
                logger.warn("%s %s %s", conn, url, e)
                conn = self.pick_conn(new=True)
                retries -= 1
                if retries < 0:
                    raise

    def gen(self, namespace, countspace):
        """
        gen_v0 generates 64bit unique ID
        timestamp = $ID >> 32
        """
        return self.gen_multi(namespace, countspace, 1)[0]

    def gen_multi(self, namespace, countspace, count):
        """
        gen_multi_v0 generates count# of 64bit unique ID list
        """
        conn = self.pick_conn()
        retries = self.max_retries
        url = "/gen?ns=%s&cs=%s&count=%d" % (namespace, countspace, count)
        while 1:
            try:
                r = conn.request("GET", url)
                content = r.data
                assert r.status == 200, "http status(%d) != 200 : %s" % (
                    r.status, content
                )
                return [int(i) for i in content.split(",")]
            except Exception as e:
                logger.warn("%s %s %s", conn, url, e)
                conn = self.pick_conn(new=True)
                retries -= 1
                if retries < 0:
                    raise

idgenerator_aws = IDGeneratorClient("AWS")
idgenerator = IDGeneratorClient()

if __name__ == "__main__":
    print(idgenerator.gen_v0("global"))
    print(idgenerator.gen_multi_v0("global", 3))
    print(idgenerator.gen("global", "group"))
    print(idgenerator.gen_multi("global", "group", 3))
