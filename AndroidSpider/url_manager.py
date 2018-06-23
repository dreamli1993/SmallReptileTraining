import queue#不能用于进程间通信
#from multiprocessing import Queue,Manager
#RuntimeError: Queue objects should only be shared between processes through inheritance,Queue队列对象不能在父进程与子进程间通信,
#另外maneger=Manager 必须放在if__name__=="__main__"后面,因此对于直接在url_manager中使用Manager.Queue()的方法也行不通
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
    def __init__(self, managerQueue = None):#managerQueue用于进程间通信,队列内部已经有锁，可以不用锁
        self.queue = queue.Queue() if managerQueue is None else managerQueue
        self.used_urls = set()#注意：多进程间进行通信时由于set类型在每个进程中都有一个副本，因此本版本中每个网页均会下载4次，可以考虑使用队列替代set

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
        temp_url = self.queue.get(timeout=5)
        return temp_url