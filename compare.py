#coding:utf8
from math import sqrt

__author__ = 'cy'
import pymongo
import urllib2
from urllib2 import urlopen
from util import connect

'''
### 读取area_coor.txt 获取地名和id的对应关系
f = open('area_coor.txt')

all_lines = f.readlines()
f.close()
result = map(lambda x: (x.split(' ')[2], x.split(' ')[3]), all_lines)
d = {}
for ii in result:
    d[ii[0].decode('utf8')] = ii[1]
'''

def get_cityid(db):
    '''
    获取墨迹天气的数据
    :param db:
    :return:
    '''
    collection = db['moji_data']
    d=db.city_id.find_one({'key':'city_id'})['data']
    ids=db.city_id.find_one({'key':'moji2mlog'})['data']
    all_cities = []
    for ii in collection.find():
        begin_time = ii['data'][u'city']['time'].replace(' ', '-').replace(':', '-').split('-')[:4]
        b = ii['data'][u'city']['cityname']
        id=ids.get(b)
        if not id:
            continue
        try:
            all_cities.append({'time': begin_time, 'info': ii['data'][u'city']['list'][0]['list'], 'id': id[0]})
        except:
            print ii
    return all_cities


def get_compare(all_cities,db):
    d=db.city_id.find_one({'key':'city_id'})['data']
    remind_info=[]
    # 获取我们的空气数据 测试只取了300个
    results={}
    for ii in all_cities[:]:
        begin_time = ''
        #[u'2015', u'12', u'12', u'20']
        for tt in ii['time']: begin_time = begin_time + tt
        end_time = ii['time'][0] + str(ii['time'][1] + str(int(ii['time'][2]) + 1)) + ii['time'][3]

        try:
            url = 'http://openapi.mlogcn.com:8000/api/aqi/fc/area/' + ii['id'] + '/h/' + begin_time + '/' + end_time + u'.json\
?appid=27fbe0976bd14ec397cd37add0526bf2&timestamp=1442477082312&key=mqC93zaI9x3whSEEasRHfOMO8bI%3D'

        except Exception as e:
            print e,ii
            continue

        r = urlopen(url)
        rr = eval(r.read())
        if 'errorCode' in rr:
            print '--------------------'
            print 'error'
            print ii, url,rr
            print '--------------------'
            continue
        mlog_data = rr['series']
        moji_data = [qq['aqi'] for qq in ii['info']]
        n= len(moji_data) if len(moji_data)<len(mlog_data) else len(mlog_data)
        mse=sqrt( float(sum(map(lambda x:(x[0]-x[1])**2, zip(moji_data,mlog_data))))/n)
        mae= ( float(sum(map(lambda x:abs(x[0]-x[1]), zip(moji_data,mlog_data))))/n)
        results[ii['id']]=(mae,mse)
    c=db.compare_results
    c.insert_one({
        'key':'moji_compare_results',
        'data':results,
        'info':u'储存与墨迹对比的结果 data是个字典 id->(mae,mse)'
    }
    )
    return remind_info


if __name__ == '__main__':
    host='54.223.178.198'#host='172.31.11.244'
    db=connect(host)
    all_cities=get_cityid(db)
    remind_info=get_compare(all_cities,db)
