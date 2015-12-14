# coding:utf8
from math import sqrt
import os
import time
import pymongo
host='54.223.178.198'
# files = ['pm2_5201512100' + str(ii) for ii in range(1, 10)]
# all_data = []
start_time = '15-11-01'
end_time = '15-11-19'
gaps = range(1, 25)
path='/home/cy/tmp/pm/'

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

def map_line(x):
    '''从文件的每一行读取有用信息'''
    res = x.split('  ')
    r0 = eval(res[0].split(' ')[-1])[1]
    r = [eval(ii)[1] for ii in res[1:]]
    r.insert(0,r0)


    return [res[0].split(' ')[0],r]

def map_24h(data):

    q=data[20::24]
    for time1 in q:
        if time1==-1:continue
        for city in time1:
            time1[city]=time1[city][0::24]
    return q
def connect(host):
    client = pymongo.MongoClient(host, 27110)
    db = client.test
    return db
def check(all_lines):
    '''
    简单的检查, 并不保证文件百分百正确, 但是出错概率极低
    :param all_lines:
    :return:
    '''
    if len(all_lines) != 1458: return False
    return all_lines[999].startswith('1475A ')

def calculate(all_data, gaps=[1], city=0):
    '''
   :param all_data: 所有的数据, 每一行代表着一个时间的数据,
   :param gaps: 所有要处理的间隔
   :param city: 监测站编号
   :return: 所有间隔(矩阵 2*len(gaps))
     '''
    results = [list(), list()]
    for gap in gaps:
        real_len = 0
        mae = mse = 0
        for ii in range(len(all_data) - gap):
            if all_data[ii] == -1 or all_data[ii + gap] == -1:
                continue
            real_len += 1
            mae += abs(all_data[ii][city][gap] - all_data[ii + gap][city][0])
            mse += (all_data[ii][city][gap] - all_data[ii + gap][city][0]) ** 2
        results[0].append(float(mae) / real_len)
        results[1].append(sqrt(float(mse) / real_len))
    return results

def write2db(db,results,start_time,end_time,city_id):
    c = db.compare_results
    c.insert_one({
       'city':city_id,
        'data':results,
        'key':'compare_results',
        'start_time':start_time,
        'end_time':end_time,
        'info':u'储存某一个城市的mse和mae'
    }  )

if __name__ == '__main__':
    all_data = []
    city_num = 1458
    files = get_files(start_time, end_time)
    for file in files:
        try:
            f = open(path + file)
            all_lines = f.readlines()
            # 按照cityid排序
            all_lines = sorted(all_lines, lambda x, y: -cmp(x.split(' ')[0], y.split(' ')[0]))
            '''if not check(all_lines):
                print 'error file '
                continue'''
            hour_info = map(map_line, all_lines)
            new_hour_info={}
            for ii in hour_info:
                new_hour_info[ii[0]]=ii[1]
            all_data.append(new_hour_info)
            f.close()
        except Exception as e:
            print e
            all_data.append(-1)

        finally:
            pass
    db=connect(host)
    c = db.compare_results
    c.delete_many({ 'key':'compare_results'})
    city_ids=db.compare_results.find_one({'key':'station_id'})['data']
    for ii in city_ids:
        results = calculate(all_data, gaps, ii)
        t_20=map_24h(all_data)
        results_24=calculate(t_20,[1],ii)
        results+=results_24
        write2db(db,results, start_time, end_time,ii)


def calculate2(all_data, gaps=[1], city=0):
    '''
   :param all_data: 所有的数据, 每一行代表着一个时间的数据,
   :param gaps: 所有要处理的间隔
   :param city: 监测站编号
   :return: 所有间隔(矩阵 2*len(gaps))
     '''
    all_data=all_data[20::24]
    results = [list(), list()]
    for gap in gaps:
        real_len = 0
        mae = mse = 0
        for ii in range(len(all_data) - gap):
            if all_data[ii] == -1 or all_data[ii + gap] == -1:
                continue
            real_len += 1
            mae += abs(all_data[ii][city][gap] - all_data[ii ][city][0])
            mse += (all_data[ii][city][gap] - all_data[ii ][city][0]) ** 2
        results[0].append(float(mae) / real_len)
        results[1].append(sqrt(float(mse) / real_len))
    return results


