#coding:utf8
__author__ = 'cy'
import pymongo
import urllib2
from urllib2 import urlopen


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


def connect(host):
    client = pymongo.MongoClient(host, 27110)
    db = client.test
    return db


# mongodb中每次采集墨迹的数据久新建一个collection, collection的名字是取值当时的时间,
#  所以对collection的名字进行排序之后, 最靠后的是一个系统的collection, 第二靠后的一个就是最新采集的墨迹空气质量信息


# city和id的对应关系写入到数据库 zhong的city_id集合中
def get_cityid(db):
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


### 获取mongodb(即墨迹)中的城市空气质量信息
# 墨迹天气中地名用的是`海淀区 `,`郑州市`,`塔里木地区`,而我们的地名是`海淀`,`郑州`,`塔里木`
# 墨迹总共采集了2500个左右的城市, 其中能在我们的数据中找到对应的有2100多个





def get_compare(all_cities,db):
    d=db.city_id.find_one({'key':'city_id'})['data']
    remind_info=[]
    # global ii, begin_time
    # 获取我们的空气数据 测试只取了300个
    for ii in all_cities[:300]:
        begin_time = ''
        for tt in ii['time']: begin_time = begin_time + tt
        end_time = ii['time'][0] + str(ii['time'][1] + str(int(ii['time'][2]) + 1)) + ii['time'][3]

        try:
            url = 'http://openapi.mlogcn.com:8000/api/aqi/fc/area/' + ii['id'] + '/h/' + begin_time + '/' + end_time + u'.json\
?appid=27fbe0976bd14ec397cd37add0526bf2&timestamp=1442477082312&key=mqC93zaI9x3whSEEasRHfOMO8bI%3D'
        except Exception as e:
            print e,ii

        r = urlopen(url)
        rr = eval(r.read())
        if 'errorCode' in rr:
            print '--------------------'
            print 'error'
            print ii, url,rr
            print '--------------------'
        mlog_data = rr['series']
        moji_data = [qq['aqi'] for qq in ii['info']]
        for ii in zip(moji_data, mlog_data):
            # 如果差距过大, 就提醒
            if float(abs(ii[0] - ii[1])) / (ii[0] + ii[1]) > 0.2 and abs(ii[0] - ii[1]) > 50:
                remind_info.append({'mlog_data': mlog_data, 'moji_data': moji_data})
    return remind_info




if __name__ == '__main__':
    host='54.223.178.198'#host='172.31.11.244'
    db=connect(host)
    all_cities=get_cityid(db)
    remind_info=get_compare(all_cities,db)
