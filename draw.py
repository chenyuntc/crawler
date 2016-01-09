# coding:utf8
#capital_num, day_num = 31, 7
import pymongo
#from util import connect
from matplotlib import pyplot as plt
import numpy as np
from ConfigParser import ConfigParser

cf=ConfigParser()
cf.read('draw.cfg')

capital_num=cf.getint('draw','capital_num')
day_num=cf.getint('draw','day_num')
station_num = cf.getint('draw','station_num')
hour_num =  (cf.getint('draw','hour_num'))
end_time=cf.get('draw','end_time')

def get_data():
    all_data2 = {}
    mongo_host = cf.get('mongodb', 'host')
    mongo_port = int(cf.get('mongodb', 'port'))
    mongo_db_name = cf.get('mongodb', 'db_name')
    client = pymongo.MongoClient(mongo_host, mongo_port)
    db = client.get_database(mongo_db_name)
    collection_name = cf.get('mongodb', 'collection')
    collection = db.get_collection(collection_name)
    for city_data in collection.find({'end_time':end_time}):
        all_data2[city_data['cityID']] = (city_data)
    capital = db.capital
    cities = capital.find_one({'key': 'capital'})
    zone = capital.find_one({'key': 'zone'})
    capital_data = {}
    for ii in cities['data']:
         capital_data[ii[0]] = all_data2[ii[4]]

    return cities ,zone,capital_data,all_data2

#capitals所有省会城市的经纬与对应的站点
# zone 华东华北东北等和所包含的省会城市
#capitals_data 省会城市的数据
# all_data:所有数据
capitals ,zone,capital_data,all_data2=get_data()

x_ticks = [ii[0] for ii in capitals['data']]
summary_data = np.zeros([24, 10])


def calculate_avg_by_file():
    '''
    计算全国所有站点的mae和mse均值
    :return:
    '''
    result=np.load('result.npz')['arr_0']
    m=result[:,:hour_num*2]

    index=(1-np.isnan(m))
    m=np.nan_to_num(m)
    m2=m*(index)
    ms=np.sum(m2,axis=0)/np.sum(index,axis=0)

    x=range(hour_num)
    plt.plot(np.array(x),ms[:hour_num],label='MAE',linewidth='2.0')
    plt.plot(x,ms[-hour_num:],label='MSE',linewidth='2.0')
    xx=range(1, 25)
    plt.xticks(xx)
    plt.title(u"所有站点 AQI数值MSE")
    plt.xlabel(u"小时")
    plt.grid(True)
    plt.xticks(xx)
    plt.legend(loc='best')
    plt.show()
def calculate_city_by_file():

    pass
def draw_avg():
    '''
    计算1500个站点所有的mae和mse
    :return:
    '''



    a = np.ones([station_num, hour_num])
    jj = 0
    for ii in all_data2.values():
        a[jj] = ii['data'][0]
        jj += 1
    a = np.array(filter(lambda x: (x[0] + 1) * x[0] != 0, a))
    avg = a.mean(axis=0)
    print avg
    summary_data[:, 0] = avg
    x = range(1, 25)
    plt.plot(x, avg, label='MAE')
    plt.title(u"所有站点 AQI数值MAE和mse")
    plt.xlabel(u"小时")
    plt.grid(True)
    a = np.ones([station_num, hour_num])
    jj = 0
    for ii in all_data2.values():
        a[jj] = ii['data'][1]
        jj += 1
    a = a[a != -1].reshape([-1, 24])
    avg = a.mean(axis=0)
    summary_data[:, 1] = avg
    plt.plot(x, avg, label='MSE',linewidth='2.0')
    print avg
    xx = range(1, 25)
    plt.xticks(xx)

    plt.title(u"所有站点 AQI数值MSE")
    plt.xlabel(u"小时")
    plt.grid(True)
    plt.xticks(xx)
    plt.legend(loc='best')
    plt.show()


def draw_level_avg():
    level_data = np.zeros([station_num, hour_num]) - 2
    jj = 0
    for ii in all_data2.values():
        kk = 0
        for iii in ii['data'][3]:
            # if ii['data'][3][kk].get('0'): level_data[jj][kk]=-1;kk+=1;continue
            level_data[jj][kk] = ii['data'][3][kk].get('0', 0)
            kk += 1
        jj += 1

    level_data = level_data[level_data != -2].reshape([-1, 24])
    avg_level = level_data.mean(axis=0)
    x = range(1, 25)
    plt.plot(x, avg_level)
    print avg_level
    summary_data[:, 2] = avg_level
    plt.title(u'AQI等级差为0(%)')
    plt.xlabel(u'小时')
    xx = range(1, 25)
    plt.xticks(xx)
    plt.grid(True)
    plt.show()


def draw_level_avg_2():
    level_data = np.zeros([station_num, hour_num]) - 2
    jj = 0
    for ii in all_data2.values():
        kk = 0
        for iii in ii['data'][3]:
            # if ii['data'][3][kk].get('0'): level_data[jj][kk]=-1;kk+=1;continue
            level_data[jj][kk] = ii['data'][3][kk].get('0', 0) + ii['data'][3][kk].get('1', 0)
            kk += 1
        jj += 1
    level_data = level_data[level_data != -2].reshape([-1, 24])
    avg_level = level_data.mean(axis=0)
    x = range(1, 25)
    plt.plot(x, avg_level)
    print avg_level
    summary_data[:, 9] = avg_level
    plt.title(u'AQI等级差为0,1(%)')
    plt.xlabel(u'小时')
    plt.grid(True)
    xx = range(1, 25)
    plt.xticks(xx)
    plt.show()

def draw_city_mse():
    '''
    话所有城市的mae 柱状图 总共话7张或者9张 ,每张包含31个城市的mae
    :return:
    '''
    city_mae = np.zeros([capital_num, day_num])
    zone_mae = {}
    jj = 0
    new_x_ticks = [ii[:-1] for ii in x_ticks]
    for ii in x_ticks:
        city_mae[jj] = capital_data[ii]['data']['day_mse']
        jj += 1

    for every_zone in zone['data']:
        max_num = []
        for every_city in zone['data'][every_zone]:
            plt.plot(np.arange(1, day_num + 1),
                     capital_data[every_city + u'市']['data']['day_mse'] ,
                     '-o', \
                     label=every_city, linewidth='2.0')
            max_num.append(max(capital_data[every_city + u'市']['data']['day_mse']))
        plt.title(every_zone + u'地区7天预测MSE')
        plt.legend(loc='best')
        plt.xlabel(u'提前天数')
        plt.ylim([0, max(max_num) * 1.1])
        plt.grid(True)
        plt.savefig(u'mse_' + unicode(every_zone))
        plt.show()


def draw_city_mae():
    '''
    话所有城市的mae 柱状图 总共话7张或者9张 ,每张包含31个城市的mae
    :return:
    '''

    city_mae = np.zeros([capital_num, day_num])
    zone_mae = {}
    jj = 0
    new_x_ticks = [ii[:-1] for ii in x_ticks]
    for ii in x_ticks:
        city_mae[jj] = capital_data[ii]['data']['day_mae']
        jj += 1

    for every_zone in zone['data']:
        max_num = []
        for every_city in zone['data'][every_zone]:
            plt.plot(np.arange(1, day_num + 1),
                     capital_data[every_city + u'市']['data']['day_mae'] ,
                     '-o', \
                     label=every_city, linewidth='2.0')
            max_num.append(max(capital_data[every_city + u'市']['data']['day_mae']))
        plt.title(every_zone + u'地区7天预测MAE')
        plt.legend(loc='best')
        plt.xlabel(u'提前天数')
        plt.ylim([0, max(max_num) * 1.1])
        plt.grid(True)
        plt.savefig(u'mae_' + unicode(every_zone))
        plt.show()



def generate_csv():
    city_mae = np.zeros([capital_num, day_num])
    city_data = {}
    zone_mae = {}
    jj = 0
    f = open('city_data.csv', 'w')
    new_x_ticks = [ii[:-1] for ii in x_ticks]
    for ii in x_ticks:
        # city_mae[jj]=capital_data[ii]['data'][2][0][:day_num]
        city_data[ii] = capital_data[ii]['data']
        jj += 1
    tmp = np.zeros([31, 18])
    jj = 0
    for ii in city_data:
        print(ii)
        tmp[jj] = city_data[ii][2][0] + city_data[ii][2][1]
        jj += 1
    for ii in range(capital_num):
        pass
    return tmp

    # plt.plot(range(1,day_num+1),city_mae[ii,:],label=x_ticks[ii])
    # if (ii!=0 and  ii%5==0) or ii==capital_num-1:
    #  plt.legend(loc='best')
    # plt.show()
