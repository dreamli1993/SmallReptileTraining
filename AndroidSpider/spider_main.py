#from AndroidSpider import url_manager, html_downloader, html_parser, html_output
import url_manager, html_downloader, html_parser, jpg_output
from bs4 import BeautifulSoup
import re
from urllib import robotparser
from urllib.parse import urljoin
from urllib.request import urlopen
from datetime import datetime
import time
from concurrent.futures import ProcessPoolExecutor,wait
import threading
import multiprocessing,os


#scrape_callback 对应self.parser.parse
class SpiderMain(object):
    def __init__(self,seed_url,user_agent = '',managerQueue=None):
        self.urls = url_manager.UrlManagerFIFO(managerQueue)
        self.downloader = html_downloader.HtmlDownLoader()
        self.parser = html_parser.HtmlParser()
        self.out_put = jpg_output.jpgOutPut()
        self.rp = get_robots(seed_url)
        self.headers = {"User-Agent":user_agent}
        self.managerQueue=managerQueue

    def craw(self, root_url, titlekey='',user_agent = ''):
        count = 0
        self.parser.root_url = root_url
        self.urls.add_new_url(root_url)
        while self.urls.has_new_url():
            try:
                new_url = self.urls.get_new_url()
                if self.rp.can_fetch(user_agent, new_url):
                    print("craw %d : %s" % (count, new_url))
                    headers = {"User-Agent":user_agent}
                    html_content = self.downloader.download(new_url, retry_count=2, headers=headers)
                    new_urls, new_data = self.parser.parse(new_url, html_content, "utf-8",titlekey)
                    self.urls.add_new_urls(new_urls)
                    if len(new_data)!=0:
                        filepath = self.out_put.parsepath(new_url)
                        self.out_put.getImg(new_data,filepath)
                    count = count + 1
            except Exception as e:
                print("craw failed!\n"+str(e))
     
    def ThreadProc(self,titlekey):
        while True:
            try:
                new_url = self.urls.get_new_url()
                if new_url is None:
                    break
                if self.rp.can_fetch(self.headers["User-Agent"], new_url):
                    try:
                        print("task:%d\tcraw : %s" % (os.getpid(),new_url))
                        html_content = self.downloader.download(new_url, retry_count=2, headers=self.headers)
                        new_urls, new_data = self.parser.parse(new_url, html_content, "utf-8",titlekey)
                        self.urls.add_new_urls(new_urls)
                        if len(new_data)!=0:
                            filepath = self.out_put.parsepath(new_url)
                            self.out_put.getImg(new_data,filepath)
                    except Exception as e:
                        print("craw failed!\n"+str(e))
            except Exception as e:
                break
    

    def ProcessProc(self,titlekey):#queue.Queue 不能用来在进程间传递消息
        threads = []
        startP = True#建立第一个线程，仅初始化有效
        while len(threads) or startP:
            # the crawl is still active
            for thread in threads:
                if not thread.is_alive():
                    # remove the stopped threads
                    threads.remove(thread)
            while (len(threads) < 4 and self.urls.has_new_url()) or startP:
                # can start some more threads
                thread = threading.Thread(target=self.ThreadProc,args=(titlekey,))
                #thread.setDaemon(True) # set daemon so main thread can exit when receives ctrl-c 后台运行
                thread.start()
                threads.append(thread)
                startP = False
            time.sleep(1)
                 
                    
    def multiProcess(self,root_url,titlekey):
        self.parser.root_url = root_url
        self.urls.add_new_url(root_url)
        ProcessPool = ProcessPoolExecutor(multiprocessing.cpu_count())
        ProList=[]
        """
        for i in range(4):
            print('create %d' % i)
            future = ProcessPool.submit(self.ProcessProc,titlekey)
            ProList.append(future)
        """
        startP=True
        while len(ProList) or startP:
            for Pro in ProList:
                if Pro.done():
                    # remove the stopped process
                    ProList.remove(Pro)
            while (len(ProList) < 4 and self.urls.has_new_url()) or startP:
                # can start some more process
                future = ProcessPool.submit(self.ProcessProc,titlekey)
                ProList.append(future)
                startP = False
            time.sleep(1)
        for result in [pro.result() for pro in ProList]:
            print("process:%s" % result)

            
    

def get_robots(url):
    """Initialize robots parser for this domain
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(urljoin(url, '/robots.txt'))
    html_ = urlopen(urljoin(url, '/robots.txt')).read().decode('utf-8',errors = 'ignore').split('\n')
    rp.parse(html_)#rp.read()解析出错UnicodeDecodeError: 'utf-8' codec can't decode byte
    return rp

def get_goals(top_url):
    """
    获取百度风云榜明星名单
    """
    try:
        #top_url = 'http://top.baidu.com/buzz?b=3'
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36"
        }
        downloader = html_downloader.HtmlDownLoader()
        html_content = downloader.download(top_url, retry_count=2, headers=headers)
    except:
        print('get top list failed')
    html_encode='utf-8'
    encodem=re.search('.+?charset=(\w+)\"',html_content.decode(html_encode,errors='ignore'))
    if encodem is not None:
        html_encode=encodem.group(1)
    soup = BeautifulSoup(html_content.decode(html_encode,errors='ignore'), "html.parser")
    links = soup.find_all("a",{'class':"list-title"}, href=re.compile('http.+?'))#使用正则表达式查找
    linksname = [link.get_text() for link in links]
    return linksname

    
if __name__ == "__main__":
    manager = multiprocessing.Manager()
    managerQueue = manager.Queue()#全局url管理器
    seed_url = 'http://www.manmankan.com'
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36"
    objSpider = SpiderMain(seed_url,user_agent=user_agent,managerQueue=managerQueue)
    #objSpider.craw(rootUrl,re_compilegoal,"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36")
    rootUrl = "http://www.manmankan.com/dy2013/mingxing/neidi/nvmingxing.shtml"
    linksname1 = get_goals('http://top.baidu.com/buzz?b=3') #获取目标
    linksname2 = get_goals('http://top.baidu.com/buzz?b=1570&fr=topboards')
    linksname = set(linksname1)|set(linksname2)
    #re_compilegoal='|'.join(set(linksname[:10]))
    re_compilegoal='|'.join(linksname)
    print(re_compilegoal)
    starttime=datetime.now()
    print('starttime:',starttime)
    objSpider.multiProcess(rootUrl,re_compilegoal)
    print('cost:',(datetime.now()-starttime).seconds)
    print('all down!')