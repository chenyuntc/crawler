# coding:utf8
__author__ = 'cy'
'''
主要实现文件的自动同步, 每周日运行, 自动获取上周日到上周六的所有数据 并处理
'''
import time
import os

data_path ='/home/ubuntu/cy/moji/data'

def get_filename():
    current_time = time.time()
    files = [time.strftime('%Y%m/%d', time.strptime(time.ctime(current_time + 3600 * i * 24))) \
                for i in      range(-7, 0, 1)]
    return  files

def get_time():
    current_time = time.time()
    times = [time.strftime('%Y-%m-%d', time.strptime(time.ctime(current_time + 3600 * i * 24))) \
                for i in  range(-7, 0, 1)]
    return  times[0], times[-1]


def sync():
    files = get_filename()
    for file in files:
        if not os.path.exists(data_path+'/'+file.split('/')[0]):print 'os';os.mkdir(data_path+'/'+file.split('/')[0])
        os.system('scp -r ubuntu@aqi-v2:~/data/jinlong.liu/AQI_new/aqi_pred/pm2_5/%s  %s/%s' \
                  % (file, data_path   ,file.split('/')[0]      ))


if __name__ == '__main__':
    sync()

