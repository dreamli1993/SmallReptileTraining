#from AndroidSpider import url_manager, html_downloader, html_parser, html_output
import url_manager, html_downloader, html_parser, jpg_output
from bs4 import BeautifulSoup
import re

class SpiderMain(object):
    def __init__(self):
        self.urls = url_manager.UrlManagerFIFO()
        self.downloader = html_downloader.HtmlDownLoader()
        self.parser = html_parser.HtmlParser()
        self.out_put = jpg_output.jpgOutPut()

    def craw(self, root_url, titlekey=''):
        count,downcount = 0,0
        self.parser.root_url = root_url
        self.urls.add_new_url(root_url)
        while self.urls.has_new_url():
            try:
                new_url = self.urls.get_new_url()
                print("craw %d : %s" % (count, new_url))
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36"
                }
                html_content = self.downloader.download(new_url, retry_count=2, headers=headers)
                new_urls, new_data = self.parser.parse(new_url, html_content, "utf-8",titlekey)
                self.urls.add_new_urls(new_urls)
                if len(new_data)!=0:
                    filepath = self.out_put.parsepath(new_url)
                    self.out_put.getImg(new_data,filepath)
                    downcount = downcount + 1
                if downcount >= 5:
                    break
                count = count + 1
            except Exception as e:
                print("craw failed!\n"+str(e))

if __name__ == "__main__":
    try:
        top_url = 'http://top.baidu.com/buzz?b=3'
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
    rootUrl = "http://www.manmankan.com/dy2013/mingxing/neidi/nvmingxing.shtml"
    for name in linksname:
        print(name+':')
        objSpider = SpiderMain()
        objSpider.craw(rootUrl,name)
    print('all down!')