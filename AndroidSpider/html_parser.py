import re
from urllib.parse import urljoin,urldefrag,urlparse
from bs4 import BeautifulSoup


class HtmlParser(object):
    #root_url = ''
    def __init__(self,root_url=''):
        self.root_url = root_url
    def parse(self, url, content, html_encode="utf-8", titlekey=''):
        if url is None or content is None:
            return
        encodem=re.search('.+?charset=(\w+)\"',content.decode(html_encode,errors='ignore'))
        if encodem is not None:
            html_encode=encodem.group(1)#抓取的网站编码为gb2312，但BeautifulSoup按照该方式解码时出现乱码，可使用gb18030，更好的方案是html解码后生成soup
        soup = BeautifulSoup(content.decode(html_encode,errors='ignore'), "html.parser")#soup = BeautifulSoup(content, "html.parser", from_encoding=html_encode)
        new_urls = self._get_new_urls(url, soup, titlekey)
        new_data = self._get_new_data(url, soup)
        return new_urls, new_data


    def _get_new_urls(self, url, soup, titlekey):
        new_urls = set()
        links = soup.find_all("a", href=re.compile('/.+?'), title=re.compile('.*?'+titlekey+'.*?'))#使用正则表达式查找
        for link in links:
            url_path = link["href"]
            url_path, _ = urldefrag(url_path)
            new_url = urljoin(url, url_path)
            if self.same_domain(new_url):
                new_urls.add(new_url)
        return new_urls


    def _get_new_data(self, url, soup):
        new_data = []
        links = soup.find_all("span", text=re.compile("http.+?\.jpg"))
        if links is not None:
            for link in links:
                jpg_path = link.get_text()
                new_data.append(jpg_path)
        return new_data
        
    def same_domain(self, url):
        return urlparse(self.root_url).netloc == urlparse(url).netloc