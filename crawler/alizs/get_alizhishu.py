# coding:utf8
import HTMLParser

__author__ = 'cy'


def get_catogery_name(d, l):
    r = []
    tmp_d = d
    for ii in l.split(','):
        r.append(tmp_d[ii]['name'])
        tmp_d = tmp_d[ii].get('children', None)
    return r


import json
import datetime


def get_data(category, d):
    '''
    获取相应的指数信息
    :param category: 种类 '1,122,3'
    :param d: 获取种类id对应的中文名称
    :return:data
    '''
    #print 'begin', category
    index, proxy = prx.get_proxy()
    r = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0',
                   'Referer': 'http://index.1688.com/alizs/market.htm?userType=purchaser&cat=51,1031817',
                   'Host': 'index.1688.com',
                   'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                   }
        url = 'http://index.1688.com/alizs/market.htm?userType=purchaser&cat=%s' % category
        r = requests.get(url, headers=headers, proxies={'http': proxy[0]}, timeout=10)

    except  requests.exceptions.BaseHTTPError as e:
        #print 'http______error%s,%s'%(str(type(e)), str(e))
        return get_data(category, d)

    except Exception as e:

        if r:
            print 'base_exception %s,%s %s' %(str(type(e)), str(e),r.url)
            return {'error': str(e)}
        else:
            return get_data(category, d)


    # prx.index=index
    prx.increase_pri(index)


    try:
        text = r.text
        soup = BeautifulSoup(text, from_encoding='utf8')
        data = soup.select('input#main-chart-val')[0].attrs['value']

        html_parser = HTMLParser.HTMLParser()
        txt = html_parser.unescape(data)
        data = eval(data)
    except Exception as e:
        print 'beautiful soup   ------------   eeeeeee %s'%str(e)
        return get_data(category,d)

    return data


import pymongo


def get_collection():
    '''
    获取collection mmdp.alizs
    :return:
    '''
    client = pymongo.MongoClient(host='54.223.101.153', port=27110)
    db = client.get_database('mmdp')
    collection = db.alizs
    return collection


def insert_data(data, collection,category):
    '''
    将数据插入到mongodb

    :param data:
    :param collection:
    :param category:
    :return:
    '''
    td = datetime.date.today()
    ty = td.year - 1
    day_1=td.day-1

    new_data = {
        'data': data,
        'category_key': category.split(','),
        'category_value': get_catogery_name(d, category),
        'end_time': td.strftime('%Y-%m-')+str(day_1),
        'start_time': str(ty) + td.strftime('-%m-%d')
    }

    collection.insert_one(new_data)


def before():
    '''
    初始化工作
    :return:
    '''
    d = json.load(open('alizhishu'))
    one = d.keys()
    two = [[ii, jj] for ii in one for jj in d[ii]['children']]
    three = [[ii[0], ii[1], jj] for ii in two \
             for jj in d[ii[0]]['children'][ii[1]].get('children', [])]


def wrap_data(category):
    r = category[0]
    for ii in category[1:]: r += ',' + ii
    return r


from bs4 import BeautifulSoup
import time
import random
from proxy import Proxy
import requests

d = json.load(open('alizhishu'))
one = d.keys()
two = [[ii, jj] for ii in one for jj in d[ii]['children']]
three = [[ii[0], ii[1], jj] for ii in two \
         for jj in d[ii[0]]['children'][ii[1]].get('children', [])]
categories = one + map(wrap_data, two) + map(wrap_data, three)
prx = Proxy()
# prx.get_online_info()
prx.load('proxies_info')

collection = get_collection()

def one_map(category):
    try:
        data = get_data(category, d)
        insert_data(data, collection,category)
    except Exception as e:
        print e
        return 0
    return 1


from multiprocessing.dummy import Pool as ThreadPool
def multi_tast(fn,lst,task_num=12):
    '''
    多线程 爬虫
    :param fn: 函数
    :param lst: list
    :param task_num: 多线程数目
    :return:
    '''

    pool = ThreadPool(task_num)
    test2 = pool.map(fn, lst)
    pool.close()
    pool.join()
    return test2

r=multi_tast(one_map,categories,400)
