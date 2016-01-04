#coding:utf8
__author__ = 'cy'
import  numpy as np
from util import   get_files
from ConfigParser import  ConfigParser
cf=ConfigParser()
cf.read('dev.cfg')
city_num=int(cf.get('calculate','city_num'))
predict_hour=int(cf.get('calculate','city_num'))




file_path=cf.get('file','filepath')
start_time=cf.get('file','start_time')
end_time=cf.get('file','end_time')
gaps=eval(cf.get('calculate','gaps'))
all_files=(get_files(start_time,end_time))
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
    new_hour_info=np.zeros([(city_num),predict_hour])-1
    all_lines = f.readlines()
    # 按照cityid排序
    all_lines = sorted(all_lines, lambda x, y: -cmp(x.split(' ')[0], y.split(' ')[0]))
    hour_info = map(map_line, all_lines)
    for ii in hour_info:
        new_hour_info[int(ii[0][:-1])-1001] = ii[1]
    f.close()
    return new_hour_info


def process_all():
    '''
    处理所有文件 , 生成一个三维数组
    第一位是预报的时刻(当前时间),第二维是城市id,第三维是提前的小时数
    :return:numpy.ndarray
    '''
    all_data=np.zeros([len(all_files),city_num,predict_hour])-1
    files=get_files(start_time,end_time)
    jj=0
    for file in files:
        print file
        try:
            new_hour_info=process_file(file)
        except Exception as e:
            print e
            continue
        all_data[jj]=new_hour_info
        jj+=1
    return all_data


def calculate_mae_mse(gap,data):
    '''
    计算mae和mse
    :param gap: int 间隔
    :param data: 数据 三维数组
    :return: mae和mse 二者都是 一维数组, 数组的长度等于city_num
    '''
    true_data=data[gap:,:,0]
    predict_data=data[:-gap,:,gap]
    # -1 代表着缺失的数据,
    valid_true_index=true_data!=-1
    valid_predict_index=predict_data!=-1
    #计算预测和实测皆不为空的index
    valid_data_index=valid_predict_index*valid_true_index

    # 计算mae
    valid_data=(np.abs(predict_data-true_data))*valid_data_index
    sum_mae=np.sum(valid_data,axis=0)/np.sum(valid_data_index,axis=0)
    #计算mse
    valid_data=((predict_data-true_data)**2)*valid_data_index
    sum_mse=np.sqrt(np.sum(valid_data,axis=0)/np.sum(valid_data_index,axis=0))

    return (sum_mae,sum_mse)
    
def calculate_level(data,gap):
    '''

    :param data:
    :param gap:
    :return:
    '''












