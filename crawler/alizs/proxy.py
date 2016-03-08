#coding:utf8
__author__ = 'cy'
import  requests
import  json

class Proxy:
    '''
    自动获取可用的代理列表
    '''
    proxies=[]
    index=0
    def __init__(self,proxies=[]):
        self.proxies=proxies
    def save(self,fname):
        '''
        把可用的代理保存成json文件
        :param fname:
        :return:
        '''
        json.dump(self.proxies,open(fname,'w'))
        return 0

    def load(self,fname):
        '''
        从文件中加载代理信息
        :param fname:
        :return:
        '''
        self.proxies=json.load(open(fname))

    def update_proxy(self):
        '''
        更新代理信息
        :return:
        '''
        self.index=0
        self.proxies=sorted(self.proxies,lambda x,y:cmp(x[1],y[1]),reverse=True)
        self.save('proxies_info')

    def increase_pri(self,index,count=1):
        self.proxies[index][1]+=count
    def decrease_pri(self,index,count=1):
        self.proxies[index][1]-=count

    def get_online_info(self):
        '''
        自动获取在线的代理信息
        :return:
        '''
        res=requests.get('http://proxy.ipcn.org/proxylist.html')
        text=res.text
        lines=text.split('\n')[73:-34]
        filter(lambda x:x.split(':')==2 and x.split('.'==4),lines)
        self.proxies=map(lambda x:['http://%s' %x ,0],lines)

    def get_proxy(self):
        '''
        返回一个可用的代理信息
        :return:代理列表 (代理的序号，代理的信息）
        '''
        self.index=(self.index+1)%len(self.proxies)
        return  self.index-1,self.proxies[self.index-1]




