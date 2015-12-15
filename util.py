#coding:utf8
import time

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


from qiniu import Auth, put_file


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
    '''
    :param start_time: 起始时间 格式如'15-12-01'
    :param end_time: 终止时间 格式同上
    :return: 所有需要处理的文件 ['pm2_5201512100','pm2_5201512101','pm2_5201512102'.....]
    '''
    s_ = start_time.split('-')
    start = int(time.strftime('%j', time.strptime(start_time, '%y-%m-%d')))
    end = int(time.strftime('%j', time.strptime(end_time, '%y-%m-%d')))
    all_files = []
    for ii in range(start, end + 1):
        tmp_time = time.strptime('15-%s' % ii, '%y-%j')
        tmp_day = time.strftime('%Y%m/%d/', tmp_time)
        tmp_day2 = time.strftime('pm2_5%Y%m%d', tmp_time)
        h_24 = ['0' + str(ii) for ii in range(10)] + [str(ii) for ii in range(10, 24)]
        b = [tmp_day + tmp_day2 + (ii) for ii in h_24]
        all_files += b
    return all_files;

def get_days(start_time, end_time):
    '''
    :param start_time: 起始时间 格式如'15-12-01'
    :param end_time: 终止时间 格式同上
    :return: 所有需要处理的文件 ['pm2_5201512100','pm2_5201512101','pm2_5201512102'.....]
    '''
    s_ = start_time.split('-')
    start = int(time.strftime('%j', time.strptime(start_time, '%y-%m-%d')))
    end = int(time.strftime('%j', time.strptime(end_time, '%y-%m-%d')))
    all_files = []
    for ii in range(start, end + 1):
        tmp_time = time.strptime('15-%s' % ii, '%y-%j')
        tmp_day = time.strftime('%Y%m/%d/', tmp_time)
        tmp_day2 = time.strftime('pm2_5%Y%m%d', tmp_time)
        b = [tmp_day + tmp_day2 ]
        all_files += b
    return all_files;
