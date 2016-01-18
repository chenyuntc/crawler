# coding:utf8
__author__ = 'cy'
import numpy as np
from util import get_files,get_hour_index,Connect_DB
from functools import partial
from get_config import *
import datetime
import math
import pymongo
import time


def map_line(x):
    '''
    """从文件的每一行读取有用信息"""
    缺失数据记录为-1
    :param x: 一行数据 str 以tab区分
    :return: [站点id,数据*241]
    '''

    res = x.split('  ')
    r0 = eval(res[0].split(' ')[-1])[1]

    r = [eval(ii)[1] for ii in res[1:]]
    r.insert(0, r0)
    return [res[0].split(' ')[0], r]


def process_file(file):
    '''
    处理文件生成一个二维数组 每一行是一个城市, 每一列是时刻
    因为站点最小的id是1001A 所以id为2027A的站点 对应的数据是d[:[2027-1001,:]
    :param file: 文件名
    :return:numpy.ndarray
    '''
    f = open(file_path + file)
    new_hour_info = np.zeros([(city_num), predict_hour]) - 1
    all_lines = f.readlines()
    # 按照cityid排序
    all_lines = sorted(all_lines, lambda x, y: -cmp(x.split(' ')[0], y.split(' ')[0]))
    hour_info = map(map_line, all_lines)
    for ii in hour_info:
        new_hour_info[int(ii[0][:-1]) - 1001] = ii[1]
    f.close()
    return new_hour_info


def process_all():
    '''
    处理所有文件 , 生成一个三维数组
    第一位是预报的时刻(当前时间),第二维是城市id,第三维是提前的小时数
    :return:numpy.ndarray
    '''
    all_data = np.zeros([len(all_files), city_num, predict_hour]) - 1
    files = get_files(start_time, end_time)
    jj = 0
    for file in files:
        print file

        try:
            new_hour_info = process_file(file)
        except Exception as e:
            jj+=1
            print(e)
            continue

        all_data[jj] = new_hour_info
        jj += 1
    return all_data


def calculate_mae_mse(data, gap):
    '''
    计算mae和mse 逐小时的
    :param gap: int 间隔
    :param data: 数据 三维数组
    :return: mae和mse 二者都是 一维数组, 数组的长度等于city_num
    '''
    try:
        true_data = data[gap:, :, 0]
        predict_data = data[:-gap, :, gap]
        # -1 代表着缺失的数据,
        valid_true_index = true_data != -1
        valid_predict_index = predict_data != -1
        # 计算预测和实测皆不为空的index
        valid_data_index = valid_predict_index * valid_true_index

        # 计算mae
        valid_data = (np.abs(predict_data - true_data)) * valid_data_index
        sum_mae = np.sum(valid_data, axis=0) / np.sum(valid_data_index, axis=0)
        # 计算mse
        valid_data = ((predict_data - true_data) ** 2) * valid_data_index
        sum_mse = np.sqrt(np.sum(valid_data, axis=0) / np.sum(valid_data_index, axis=0))
    except Exception as e:
        print e
        return np.zeros([city_num, 1]) - 1, np.zeros([city_num, 1]) - 1

    return (sum_mae, sum_mse)


def test_mae_mse(true_data, predict_data):
    valid_true_index = true_data != -1
    valid_predict_index = predict_data != -1
    # 计算预测和实测皆不为空的index
    valid_data_index = valid_predict_index * valid_true_index

    # 计算mae
    valid_data = (np.abs(predict_data - true_data)) * valid_data_index
    sum_mae = np.sum(valid_data, axis=0) / np.sum(valid_data_index, axis=0)
    # 计算mse
    valid_data = ((predict_data - true_data) ** 2) * valid_data_index
    sum_mse = np.sqrt(np.sum(valid_data, axis=0) / np.sum(valid_data_index, axis=0))

    return np.zeros([city_num, 1]) - 1, np.zeros([city_num, 1]) - 1

    return (sum_mae, sum_mse)


def calculate_level(data, gap):
    '''
    :param data:数据 三维数组
    :param gap: 间隔 int
    :return: 二维数组 city_num*len(bins) 每个城市的每个等级差所占的比例
    每一行的元素[0.2,0.6,0.4,0,0]  第一个元素是缺失的数据比例, 第二个元素是预测准确的比例, 第三个是预测等级差为1的比例
    '''

    try:
        true_level_data = np.floor(data[gap:, :, 0] / 50)
        predict_level_data = np.floor(data[:-gap, :, gap] / 50)
        # -1 代表着缺失的数据,
        valid_true_index = true_level_data > 0
        valid_predict_index = predict_level_data > 0
        # 计算预测和实测皆不为空的index
        valid_data_index = valid_predict_index * valid_true_index

        result = (1 + np.abs(predict_level_data - true_level_data)) * (valid_data_index)
        bins = eval(cf.get('calculate', 'bins'))

        level_result = np.zeros([true_level_data.shape[1], len(bins)])

        level_dist = map(lambda x: np.array(np.histogram(x, bins=bins)[0], \
                                            dtype=float) / sum(np.histogram(x, bins=bins)[0][1:]), result.T)
    except Exception as e:
        print e
        return np.zeros([city_num, len(bins)]) - 1

    return np.array(level_dist)


def calculate_mean_by_day(data):
    '''
    把逐小时的数据变成逐日,并清楚无效数据
    :param data: array city_num*hour_num
    :return:
    '''
    data_by_day = (data.reshape([data.shape[0], -1, 24]))
    valid_data_index_by_day = data_by_day != -1
    sum_data_by_day = np.sum(data_by_day * valid_data_index_by_day, axis=2)
    valid_hour_num_by_day = np.sum(valid_data_index_by_day, axis=2)
    data_by_day = sum_data_by_day / valid_hour_num_by_day
    return data_by_day


def calculate_day_mae_mse(data, gap):
    try:
        true_data = (data[gap * 24:, :, 0]).T
        predict_data = data[21:-gap * 24:24, :, 3 + (gap - 1) * 24:3 + (gap) * 24]
        # 多维矩阵的转置 之前predict_data shape是(4,1711,24) 装置成和true_data一样的形状
        # (1711,96)
        predict_data = np.transpose(predict_data, (1, 0, 2))
        predict_data = predict_data.reshape([predict_data.shape[0], -1])

        # 计算逐日的平均值,需注意剔除无效数据

        predict_by_day = calculate_mean_by_day(predict_data)
        true_by_day = calculate_mean_by_day(true_data)
        ##### TODO: 是否需要再判断里面有缺失的数据
        predict_by_day = np.nan_to_num(predict_by_day)
        true_by_day = np.nan_to_num(true_by_day)

        valid_true_index = true_by_day != 0
        valid_predict_index = predict_by_day != 0
        # 计算预测和实测皆不为空的index
        valid_data_index = valid_predict_index * valid_true_index
        predict_by_day=predict_by_day*valid_data_index
        true_by_day=true_by_day*valid_data_index

        mae = np.sum(np.abs(predict_by_day - true_by_day), axis=1) / np.sum(valid_data_index, axis=1)
        mse = np.sqrt(np.sum((predict_by_day - true_by_day) ** 2, axis=1) \
                      / np.sum(valid_data_index, axis=1))
        print
    except  Exception as e:
        print '---------------error-------------'
        print e
        mse = mae = np.zeros([city_num, 1]) - 1

    return mae, mse


def h_stack_data(mae_mse_by_hours, level_by_hours, day_mae_mse):
    '''
    把所有的数据拼接起来
    :param mae_mse_by_hours:
    :param level_by_hours:
    :param day_mae_mse:
    :return:
    '''
    maes = np.vstack((mae_mse[0] for mae_mse in mae_mse_by_hours)).T
    mses = np.vstack((mae_mse[1] for mae_mse in mae_mse_by_hours)).T
    level_datas = np.hstack((level_data for level_data in level_by_hours))
    day_maes = np.vstack((mae_mse[0] for mae_mse in day_mae_mse)).T
    day_mses = np.vstack((mae_mse[1] for mae_mse in day_mae_mse)).T
    results = np.hstack((maes, mses, level_datas, day_maes, day_mses))
    return results

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

if __name__ == '__main__':
    data = process_all()
    coll=Connect_DB()
    mongo_data=ReadOneStation(coll,start_time,end_time)
    wrap(data,mongo_data)
    # 使用偏函数 固定data,便于之后map操作
    #data = np.load('2015_12_30.npz')['arr_0']

    cal_mae_mse = partial(calculate_mae_mse, data)
    cal_level = partial(calculate_level, data)
    cal_day_mae_mse = partial(calculate_day_mae_mse, data)

    mae_mse_by_hours = map(cal_mae_mse, gaps)
    level_by_hours = map(cal_level, gaps)
    day_mae_mse = map(cal_day_mae_mse, day_gaps)

    results = h_stack_data(mae_mse_by_hours, level_by_hours, day_mae_mse)
    insert_to_mongo(db, results)
