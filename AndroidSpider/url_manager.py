import queue
#UrlManager方法访问随机（set方法内部为hash存储）
class UrlManager(object):
    def __init__(self):
        self.new_urls = set()
        self.used_urls = set()

    def add_new_url(self, url):
        if url is None:
            return
        if url not in self.new_urls and url not in self.used_urls:
            self.new_urls.add(url)

    def add_new_urls(self, urls):
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_new_url(url)

    def has_new_url(self):
        return len(self.new_urls) > 0

    def get_new_url(self):
        temp_url = self.new_urls.pop()
        self.used_urls.add(temp_url)
        return temp_url

class UrlManagerFIFO(object):
    def __init__(self):
        self.queue = queue.Queue()
        self.used_urls = set()

    def add_new_url(self, url):
        if url is None:
            return
        if url not in self.used_urls:
            self.used_urls.add(url)
            self.queue.put(url)

    def add_new_urls(self, urls):
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_new_url(url)

    def has_new_url(self):
        return self.queue.qsize() > 0

    def get_new_url(self):
        temp_url = self.queue.get()
        return temp_url