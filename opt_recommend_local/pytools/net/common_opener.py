#coding=utf8

import urllib2
import urllib
import cookielib
from gzip import GzipFile
from StringIO import StringIO
from urllib2 import BaseHandler, HTTPHandler, HTTPDefaultErrorHandler, HTTPError
import sys, httplib, socket, time
import zlib

class HTTPErrorRetryHandler(HTTPHandler, HTTPDefaultErrorHandler):
    def __init__(self, timeout=None, retry=0, interval=30, retry_code=[]):
        HTTPHandler.__init__(self)
        self.timeout = timeout
        self.retry = retry
        self.interval = interval
        self.retry_code = retry_code

    def http_error_default(self, req, fp, code, msg, hdrs):
        if hasattr(req, 'retry') and req.retry > 0:
            if code in self.retry_code:
                #print 'Http error occur %s %s, retry after %s seconds' % (code, msg, self.interval)
                time.sleep(self.interval)
                req.retry -= 1
                return self.parent.open(req)
        raise HTTPError(req.get_full_url(), code, msg, hdrs, fp)

    def http_request(self, req):
        req = HTTPHandler.http_request(self, req)
        return req

    def http_open(self, req):
        timeout = hasattr(req, 'timeout') and req.timeout or self.timeout
        if timeout:
            req.timeout = timeout

            # Check the python version
            #if sys.version_info[0] == 2 and sys.version_info[1] > 5:
            #    req.timeout = timeout
            #else:
            #    # May cause some unexpected result
            #socket.setdefaulttimeout(float(timeout))

        if not self.retry:
            return self.do_open(httplib.HTTPConnection, req)

        if not hasattr(req, 'retry'):
            req.retry = self.retry

        while True:
            try:
                return self.do_open(httplib.HTTPConnection, req)
            except Exception, e:
                if req.retry > 0:
                    req.retry -= 1
                    time.sleep(self.interval)
                else:
                    raise e

class CommonHeaderHandler(BaseHandler):
    """A handler to add gzip capabilities to urllib2 requests """
    def __init__(self, http_headers=None, use_common_headers=True):
        self.http_headers = {}
        if use_common_headers:
            self.http_headers["Accept-Encoding"] = "gzip, deflate"
            self.http_headers["Accept"] =  "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            self.http_headers["Accept-Language"] = "zh-cn,zh;q=0.5"
            self.http_headers["User-Agent"] = "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3"
            self.http_headers["Accept-Charset"] = "GB2312,utf-8;q=0.7,*;q=0.7"
            self.http_headers["Connection"] = "keep-alive"
            self.http_headers["Cache-Control"] = "max-age=0"
        if http_headers:
            self.http_headers.update(http_headers)

    def http_request(self, req):
        for header, value in self.http_headers.iteritems():
            if value:
                req.add_unredirected_header(header, value)
        return req


    def http_response(self, req, resp):
        # Decode gzip
        if resp.headers.get("content-encoding") == "gzip":
            gz = GzipFile(fileobj=StringIO(resp.read()), mode="r")
        # Decode deflate
        elif resp.headers.get("content-encoding") == "deflate":
            data = resp.read()
            try:
                data = zlib.decompress(data, -zlib.MAX_WBITS)
            except zlib.error:
                data = zlib.decompress(data)
            gz = StringIO(data)
        else:
            return resp

        old_resp = resp
        resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url)
        resp.code = old_resp.code
        resp.msg = old_resp.msg
        return resp

class DynamicProxyHandler(urllib2.ProxyHandler):
    '''support dynamic proxy: provide a callable to dynamically choose a proxy'''

    def __init__(self, proxies=None):
        urllib2.ProxyHandler.__init__(self, proxies=proxies)

    def proxy_open(self, req, proxy, type):
        if callable(proxy):
            proxy = proxy()
        
        urllib2.ProxyHandler.proxy_open(self, req, proxy, type)

    def http_response(self, req, resp):
        resp.host = req.host
        return resp

def get_opener(timeout=None, use_cookie=True, http_proxy=None, https_proxy=None,
        retry=0, interval=30, retry_code=[], http_headers=None, use_common_headers=True):
    handlers = []

    if use_cookie:
        cj = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor(cj)
        handlers.append(handler)

    proxy = {}
    if http_proxy:
        proxy['http'] = http_proxy
    if https_proxy:
        proxy['https'] = https_proxy
    if proxy:
        handler = DynamicProxyHandler(proxy)
        handlers.append(handler)

    if retry or timeout:
        handler = HTTPErrorRetryHandler(
                timeout=timeout,
                retry=retry,
                interval=interval,
                retry_code=retry_code)
        handlers.append(handler)

    # May change in higher python version
    if timeout:
        socket.setdefaulttimeout(float(timeout))

    common_header_handler = CommonHeaderHandler(
            http_headers=http_headers, 
            use_common_headers=use_common_headers)
    handlers.append(common_header_handler)

    opener = urllib2.build_opener(*handlers)
    return opener

if __name__ == '__main__':
    from pyutil.net.proxy import get_proxy
    urllib2.install_opener(get_opener(http_proxy=get_proxy, use_common_headers=False))
    url = 'http://v.youku.com/v_show/id_XNDI3NjQzNTg4.html?f=17837580'
    req = urllib2.Request(url)
    try:
        f = urllib2.urlopen(req)
        print f.url, f.code, f.read()[:1000]
        print req.header_items()
        print f.host
    except Exception,e:
        print e.fp.host
        print e.code
