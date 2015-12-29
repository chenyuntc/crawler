#coding:utf8
from math import sqrt

__author__ = 'cy'


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
            if all_data[ii] == -1 or all_data[ii + gap] == -1\
                    or all_data[ii].has_key(city)==False or all_data[ii + gap].has_key(city)==False:
                continue
            real_len += 1
            mae += abs(all_data[ii][city][gap] - all_data[ii + gap][city][0])
            mse += (all_data[ii][city][gap] - all_data[ii + gap][city][0]) ** 2
        if real_len==0:
            results[0].append(-1)
            results[1].append(-1)
        else:
            results[0].append(float(mae) / real_len)
            results[1].append(sqrt(float(mse) / real_len))
    return results


def calculate_level(all_data, gaps=[1], city=0):
    '''
    统计等级差出现的次数
   :param all_data: 所有的数据, 每一行代表着一个时间的数据,
   :param gaps: 所有要处理的间隔
   :param city: 监测站编号
   :return: 所有间隔(矩阵 2*len(gaps))
     '''

    results=[]
    for gap in gaps:
        real_len = 0
        tmp={};dist=[]
        for ii in range(len(all_data) - gap):
            if all_data[ii] == -1 or all_data[ii + gap] == -1\
                    or all_data[ii].has_key(city)==False or all_data[ii + gap].has_key(city)==False:
                continue
            real_len += 1
            dist.append(abs(all_data[ii][city][gap]/50 - all_data[ii + gap][city][0]/50))
        if len(dist)==0:
            tmp['-1']=1
            results.append(tmp)
            continue

        for ii in range(max(dist)+1):
            if dist.count(ii)>0:
                tmp[str(ii)]=float(dist.count(ii))/(real_len)
        results.append(tmp)
    return results


def calculate2(x, y):
    '''
    计算两个组数据的mae和mse,数据中缺失值用-1 表示
    :param x: 第一组数据
    :param y: 第二组
    :return:(mae,mse)
    '''
    f = filter(lambda x: (x[0] + 1) * (x[1] + 1) != 0, zip(x, y))
    mse = map(lambda x: (x[0] - x[1]) ** 2, f)
    mae = map(lambda x: abs(x[0] - x[1]), f)
    c = len(f)
    if c==0:
        return [-1,-1]
    mae = reduce(lambda a, b: a + b, mae)
    mse = reduce(lambda a, b: a + b, mse)

    return [float(mae) / c, sqrt(float(mse) / c)]