#coding:utf8
import numpy as np
from get_config import city_num, cf


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