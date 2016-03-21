#coding:utf8
'''
爬取彩云的数据并写文件,(格式化和源文件)
每小时爬取
'''
import json
import os
from urllib2 import urlopen
import time
import pymongo

path='/home/ubuntu/cy/moji/moji/aqi/caiyun/'
host='54.223.101.153'
port=27110
__author__ = 'cy'
def connect(host,port=27110):
    client = pymongo.MongoClient(host, port)
    db = client.test
    return db


def get_data(location):
    url = 'http://api.caiyunapp.com/v2/Y2FpeXVuIGFuZHJpb2QgYXBp/%s/forecast?lang=zh_CN' % location
    r = urlopen(url,timeout=10)
    res = r.read()
    return res

def get_station():
    client=pymongo.MongoClient('54.223.178.198',27110)
    db=client.test
    c=db.stations
    stations=[]
    for ii in c.find():
        stations.append((ii['code'],ii['longtitude'],ii['latitude']))
    return stations

def format_data(data,station_id):
    data=json.loads(data)
    hourly_data=data['result']['hourly']
    tt=map(lambda x:x['datetime'],hourly_data['aqi'])
    aqi=map(lambda x:x['value'],hourly_data['aqi'])
    pm25=map(lambda x:x['value'],hourly_data['pm25'])
    skycon=map(lambda x:x['value'],hourly_data['skycon'])
    cloudrate=map(lambda x:x['value'],hourly_data['cloudrate'])
    humidity=map(lambda x:x['value'],hourly_data['humidity'])
    precipitation=map(lambda x:x['value'],hourly_data['precipitation'])
    wind=map(lambda x:(x['direction'],x['speed']),hourly_data['wind'])
    temperature=map(lambda x:x['value'],hourly_data['temperature'])
    result=map(lambda x:{
        't':x[0],
        'aqi':x[1],
        'pm25':x[2],
        'skycon':x[3],
        'cloudreate':x[4],
    'humidity':x[5],
    'precipitation':x[6],
        'wind':x[7],
        'temperature':x[8]},zip(tt,aqi,pm25,skycon,cloudrate,humidity,precipitation,wind,temperature))
    return str(station_id)+'\t'+json.dumps(result)


def get_city(db):
    c = db.city
    cities = []

    for ii in c.find({"country.id": 642672}):
        cities.append(ii)
    return cities


def main():
    t = time.strftime('%Y%m%d')
    file_name = time.strftime('%H.txt')
    raw_dir, formatted_dir = path + t + '/raw/', path + t + '/formatted/'
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)
        os.makedirs(formatted_dir)
    db = connect(host, port)
    client = pymongo.MongoClient(host, port)
    cities = get_city(client.mmdp)
    stations = get_station()
    for ii in stations:
        print 'process city %s ' % ii[0]
        station_id = ii[0]
        try:
            data = get_data('%s,%s' % (ii[1], ii[2]))
        except Exception as e:
            print e;
            continue

        with open(raw_dir + file_name, 'a') as f:
            data = json.loads(data)
            data = json.dumps(data) + '\r\n'
            f.write(data)
        try:
            formatted_data = format_data(data, station_id)
        except Exception as e:
            print e
            continue
        with open(formatted_dir + file_name, 'a') as f:
            f.write(formatted_data + '\r\n')


if __name__ == '__main__':
    try:
        main()
    except:
        print e

