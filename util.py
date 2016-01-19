#coding:utf8
import datetime
import math
import time
from get_config import start_time, end_time, gaps, bins, day_gaps, city_num, collection_name

__author__ = 'cy'
import pymongo

def station_csv2db(file):
    '''
    把csv中的站点信息写入数据库 ,
    第一行必须得是 标题栏,另存为csv, 以逗号分隔
    :param file:
    :return: 字典  station code->[cityname,stationname,latitude,longtitude]
    '''
    f=open(file)
    info=open(file).readlines()
    data=map(lambda x:x.strip().decode('utf8').split(','),info)
    result={}
    reduce(lambda x,y:result.update({y[-1]:y[0:-1]}),data)
    return result

    '''
    data=[]
    for ii in result:
    tmp={
    'code':ii,
    'area':result[ii][0],
    'positionName':result[ii][1],
    'latitude':result[ii][2],
    'longtitude':result[ii][3]}
    data.append(tmp)
    collection.insert_many(data)
'''

def Connect_DB():
    # 连接mongodb数据库
    entry = 'mongodb://54.223.178.198:27110/'
    Client = pymongo.MongoClient(entry)
    db = Client.pm25_data
    collection = db.pm25in

    return collection
from qiniu import Auth, put_file
def get_hour_index(start,end):
    '''
    计算两个时间之间差多少天
    :param start: '2016-12-09 12'
    :param end: 格式同上
    :return:Int
    '''
    start_time = time.mktime(time.strptime(start, '%Y-%m-%d %H'))
    end_time = time.mktime(time.strptime(end, '%Y-%m-%d %H'))
    return (end_time - start_time) / 3600

def qiniu_upload(data,key,mimeType):
    '''
    上传文件
    :param data: 要上传的数据路径 ../pic/info.jpg
    :param key: 上传之后的文件名   info2015.jpg
    :return: 图片的url
    '''
    sk = 'qe6rrhgxsLL9D3HSen5XMh5U_kDkv8C79JKyvicx'
    ak = 'hExG9puYF2O_L7YgDCuDJmiYgfCfosmjNqAWjIMG'
    bucket = 'cloudscape'
    q = Auth(ak, sk)
    #key = 'a.jpg'
    #mimetype='image/jpeg'
    token = q.upload_token(bucket, key)
    #data = 'pictures/lena.jpg'
    put_file(token, key, data, mime_type=mimeType, check_crc=True)
    return 'http://cloudscape.qiniudn.com/%s' %key

#qiniu_upload()

def connect(host,port=27110):
    client = pymongo.MongoClient(host, port)
    db = client.test
    return db



def get_files(start_time, end_time):
    # FIXED TODO : 目前只能处理2015 年 的时间
    '''
    :param start_time: 起始时间 格式如'2015-12-01'
    :param end_time: 终止时间 格式同上
    :return: 所有需要处理的文件 ['pm2_5201512100','pm2_5201512101','pm2_5201512102'.....]
    '''
    start_time=time.mktime(time.strptime(start_time,'%Y-%m-%d'))
    end_time=time.mktime(time.strptime(end_time,'%Y-%m-%d'))+1
    all_files = []
    for every_day in xrange(int(start_time),int(end_time),86400):
        tmp_time=time.strptime(time.ctime(every_day))
        tmp_day=time.strftime('%Y%m/%d/',tmp_time)
        tmp_day2 = time.strftime('pm2_5%Y%m%d', tmp_time)
        tmp_day3=time.strftime('%Y%m%d', tmp_time)
        h_24 = ['0' + str(ii) for ii in range(10)] + [str(ii) for ii in range(10, 24)]
        #b = [tmp_day + tmp_day2 + (ii) for ii in h_24]
        b=[tmp_day3+(ii)+'.sent' for ii in h_24]
        all_files += b
    return all_files;


def ReadOneStation(collection ,str_start,str_now):
    '''
    start_time=2015-11-01
#计算的终止时间
end_time=2015-11-06
    :param collection:
    :param str_start:
    :param str_now:
    :return:
    '''
    time_start = datetime.datetime.strptime(str_start+'00',"%Y-%m-%d%H")
    stamp_start = math.floor(time.mktime(time_start.timetuple()))
    time_now = datetime.datetime.strptime(str_now+'00',"%Y-%m-%d%H")
    stamp_now = math.floor(time.mktime(time_now.timetuple()))
    aqi_data_tmp = collection.find({'station_code':{'$lte':'2710A'},
                                    "timestamp":{"$gte":math.floor(stamp_start),'$lte':math.floor(stamp_now)},\
                                    "aqi":{"$gt":0}},\

                                   {"timestamp":"true","aqi":"true","time_point":"true","_id":0,'station_code':'true'})\
        .hint([("station_code", pymongo.ASCENDING),('timestamp', pymongo.ASCENDING)])
    return aqi_data_tmp


def insert_to_mongo(db, results):
    '''
    重新整合数据, 插入到mongodb中
    :param db:
    :param results:
    :return:
    '''
    all_data = [{
                    'key': 'calculate_results',
                    'cityID': str(city + 1001) + 'A',
                    'start_time': start_time,
                    'end_time': end_time,
                    'info': '储存从start_time 到end_time的计算结果',
                    'data': {
                        'mae': list(result[:len(gaps)]),
                        'mse': list(result[len(gaps):2 * len(gaps)]),
                        'levels': map(lambda x: list(x), list(result[2 * len(gaps):2 * len(gaps) + \
                        (len(bins) - 1) * len(gaps)].reshape(
                            [len(gaps), -1]))),
                        'day_mae': list(result[2 * len(gaps) + (len(bins) - 1) * len(gaps): \
                            2 * len(gaps) + (len(bins) - 1) * len(gaps) + len(day_gaps)]),
                        'day_mse': list(result[-len(day_gaps):])

                    }

                } for (result, city) in zip(results, xrange(city_num))
                ]
    col = db.get_collection(collection_name)

    col.insert_many(all_data)


def wrap(data,mongo_data):
    for ii in mongo_data:
        real_time=ii['time_point'].split(':')[0]
        now_time=time.strftime('%Y-%m-%d %H', time.strptime(real_time,'%Y-%m-%dT%H'))
        index=get_hour_index(start_time+' 00',now_time)
        data[index][int(ii['station_code'][:-1])-1001][0]=ii['aqi']