import urllib.request
import os
class jpgOutPut(object):
    def mkdir(self,dirnames):
        curpath=os.path.abspath('.')
        for dirname in dirnames:
            curpath = os.path.join(curpath, dirname)
            if os.path.exists(curpath):
                continue
            else:
                os.mkdir(curpath)
        return curpath  

    def parsepath(self,url):
        try:
            pathlists = url.split('//')[1].split('/')[1:]
            pathlist = pathlists[:-1]
            pathlist.append(pathlists[-1].split('.')[0])#pathlist = pathlists[:-1].append(pathlists[-1].split('.')[0])有错，返回为空
        except Exception as e:
            pathlist = []
        finally:
            return self.mkdir(pathlist)
    def getImg(self,imgList,dirpath):
        x = 0
        for imgurl in imgList:
            #print ("for test %s" % x) 查看是否走到循环用的print
            #urlretrieve() 方法直接将远程数据下载到本地
            urllib.request.urlretrieve(imgurl,os.path.join(dirpath,'%s.jpg' % x))
            x += 1