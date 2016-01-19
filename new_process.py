# coding:utf8
from calculate import calculate_mae_mse, calculate_level, calculate_day_mae_mse

__author__ = 'cy'
from functools import partial

import numpy as np

from util import Connect_DB, ReadOneStation, insert_to_mongo, wrap
from get_config import *


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
            jj += 1
            print(e)
            continue

        all_data[jj] = new_hour_info
        jj += 1
    return all_data


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


if __name__ == '__main__':
    data = process_all()
    coll=Connect_DB()
    mongo_data= ReadOneStation(coll,start_time,end_time)
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
