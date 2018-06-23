from http import cookiejar
from urllib import request, error
from urllib.parse import urlparse
import time
from datetime import datetime, timedelta
import socket

DEFAULT_DELAY = 0
DEFAULT_TIMEOUT = 60

class HtmlDownLoader(object):
    def __init__(self, delay=DEFAULT_DELAY, timeout=DEFAULT_TIMEOUT):
        socket.setdefaulttimeout(timeout)
        self.throttle = Throttle(delay)

    def download(self, url, retry_count=3, headers=None, proxy=None, data=None):
        if url is None:
            return None
        try:
            self.throttle.wait(url)#延时
            req = request.Request(url, headers=headers, data=data)
            cookie = cookiejar.CookieJar()
            cookie_process = request.HTTPCookieProcessor(cookie)
            opener = request.build_opener()
            if proxy:
                proxies = {urlparse(url).scheme: proxy}
                opener.add_handler(request.ProxyHandler(proxies))
            content = opener.open(req).read()
        except error.URLError as e:
            print('HtmlDownLoader download error:', e.reason)
            content = None
            if retry_count > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    #说明是 HTTPError 错误且 HTTP CODE 为 5XX 范围说明是服务器错误，可以尝试再次下载
                    return self.download(url, retry_count-1, headers, proxy, data)
        return content

class Throttle:
    """Throttle downloading by sleeping between requests to same domain
    """
    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}
        
    def wait(self, url):
        """Delay if have accessed this domain recently
        """
        domain = urlparse(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()
