# coding:utf8
import time

__author__ = 'cy'
import pymongo
import numpy as np
from functools import partial

data_day_num = 5  # 预测的天数
predict_day_num = 10  # 提前多少天预测

_sh = '58367'
_bj = '54511'
_sz = '59493'
_gz = '59287'
start_time = "2016-01-06"
end_time = "2016-01-10"
day_gap = 4


def get_date_index(start, end_time):
    start_time = time.mktime(time.strptime(start, '%Y-%m-%d'))
    end_time = time.mktime(time.strptime(end_time, '%Y-%m-%d'))
    return (end_time - start_time) / 86400


def get_time(start_time, end_time):
    # FIXED
    '''
    :param start_time: 起始时间 格式如'2015-12-01'
    :param end_time: 终止时间 格式同上
    :return: 在此之间的每一天
    '''
    start_time = time.mktime(time.strptime(start_time, '%Y-%m-%d'))
    end_time = time.mktime(time.strptime(end_time, '%Y-%m-%d')) + 1
    all_days = []
    for every_day in xrange(int(start_time), int(end_time), 86400):
        tmp_time = time.strptime(time.ctime(every_day))
        tmp_day = time.strftime('%Y-%m-%d', tmp_time)
        all_days.append(tmp_day)
    return all_days;


def connect(host='54.223.101.153', port=27110, db='mmdp', collection='realtime_day'):
    '''
    连接数据库 返回collection对象
    :param host:
    :param port:
    :param db:
    :param collection:
    :return:
    '''
    col = None
    try:
        client = pymongo.MongoClient(host, port)
        db = client.get_database(db)
        col = db.get_collection(collection)
    except Exception as e:
        print e
    return col if col else -1


def get_city_data(city_id, collection_name):
    '''
    根据城市的id返回这个城市的所有预测数据
    :param city_id:
    :return:
    '''
    col = connect(collection=collection_name)
    data = col.find({'poi.id': city_id, 'createDate': {'$gte': start_time, '$lte': end_time}})
    return data


def wrap(realtime):
    result = {}
    for ii in realtime:
        result[ii['date']] = ii
    return result


def wrap2(twc_data, minTemp='minTemp', maxTemp='maxTemp'):
    minTemp_info = np.zeros([data_day_num, predict_day_num]) + 100
    maxTemp_info = np.zeros([data_day_num, predict_day_num]) + 100
    for ii in twc_data:
        x_index = get_date_index(start_time, ii['createDate'])
        y_index = get_date_index(ii['createDate'], ii['date'])
        minTemp_info[x_index][y_index] = ii[minTemp]
        maxTemp_info[x_index][y_index] = ii[maxTemp]

    return maxTemp_info, minTemp_info


def get_true_data(city_id, minTemp='minTemp', maxTemp='maxTemp'):
    col = connect(collection='realtime_day')
    realtime = col.find({'poiId': city_id, 'date': {'$gte': start_time,'$lte':end_time}})
    true_data = np.array([[ii['maxTemp'], ii['minTemp']] for ii in realtime])
    return true_data


def get_predict_data(city_id, collection='twc_day', minTemp='minTemp', maxTemp='maxTemp'):
    twc_data = get_city_data(city_id, collection).sort \
        ([('createDate', pymongo.ASCENDING), \
          ('date', pymongo.ASCENDING)])
    predict_data = wrap2(twc_data, minTemp, maxTemp)
    return predict_data


def calculate_mae_mse(data, gap):
    leng = data.shape[0]
    predict_data = data[:leng - gap, gap + 1]
    valid_predict_data_index = predict_data != 100
    valid_predict_data = predict_data * valid_predict_data_index
    mae = np.sum(np.abs(data[gap:, 0] - valid_predict_data) * valid_predict_data_index) \
          / np.sum(valid_predict_data_index)
    mse = np.sqrt(np.sum((data[gap:, 0] * valid_predict_data_index - valid_predict_data) ** 2) \
                  / np.sum(valid_predict_data_index))

    return mae, mse


def calculate_all():
    gaps = xrange(day_gap)
    # 计算twc
    predict_data = get_predict_data('59493')
    true_data = get_true_data('59493')

    tempMax = np.hstack((true_data[:, 0].reshape([data_day_num, 1]), predict_data[0]))
    tempMin = np.hstack((true_data[:, 1].reshape([data_day_num, 1]), predict_data[1]))
    max_map = partial(calculate_mae_mse, tempMax)
    min_map = partial(calculate_mae_mse, tempMin)

    max_temp1 = map(max_map, gaps)
    min_temp1 = map(min_map, gaps)
    # return  max_temp,min_temp
    # 计算象辑
    predict_data = get_predict_data('59493', 'xiangji_day', 'tmpMin', 'tmpMax')

    tempMax = np.hstack((true_data[:, 0].reshape([data_day_num, 1]), predict_data[0]))
    tempMin = np.hstack((true_data[:, 1].reshape([data_day_num, 1]), predict_data[1]))
    max_map = partial(calculate_mae_mse, tempMax)
    min_map = partial(calculate_mae_mse, tempMin)

    max_temp = map(max_map, gaps)
    min_temp = map(min_map, gaps)
    return max_temp1, min_temp1, max_temp, min_temp


# calculate_all()
#data = calculate_all()


def