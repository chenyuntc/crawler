#coding:utf8
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
csv_by_hour=np.zeros([hour_num,5])
csv_by_city=np.zeros([capital_num,2*day_num])


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

    x=range(1,1+hour_num)

    csv_by_hour[:,0]=ms[:hour_num]
    csv_by_hour[:,1]=ms[-hour_num:]

    plt.plot(np.array(x),ms[:hour_num],label='MAE',linewidth='2.0')
    plt.plot(x,ms[-hour_num:],label='MSE',linewidth='2.0')
    xx=range(1, 25)
    plt.xticks(xx)
    plt.title(u"所有站点 AQI数值")
    plt.xlabel(u"小时")
    plt.grid(True)
    plt.xticks(xx)
    plt.legend(loc='best')
    plt.savefig(u'所有站点数据平均.png')
    plt.grid(True)
    plt.show()



def draw_level_avg():
    '''
    画所有城市的等级差的平均值
    :return:
    '''
    level_data = np.zeros([1711, hour_num]) - 2
    jj = 0
    for ii in all_data2.values():
        kk = 0
        for iii in ii['data']['levels']:
            level_data[jj][kk] = ii['data']['levels'][kk][1]
            kk += 1
        jj += 1
    index=level_data != -2
    level_data = level_data*index
    #level_data=level_data[level_data != np.inf].reshape([-1, 24])
    index1=level_data!=np.inf
    index=index1*index
    level_data=np.nan_to_num(level_data)
    level_data2=level_data*index

    avg_level =(level_data2).sum(axis=0)/np.sum(index,axis=0)
    x = range(1, 25)
    plt.plot(x, avg_level,label=u"预测准确",linewidth='2.0')
    csv_by_hour[:,2] = avg_level
    summary_data[:, 2] = avg_level
    tmp_level=avg_level

    level_data = np.zeros([1711, hour_num]) - 2
    jj = 0
    for ii in all_data2.values():
        kk = 0
        for iii in ii['data']['levels']:
            level_data[jj][kk] = ii['data']['levels'][kk][1]+ii['data']['levels'][kk][2]
            kk += 1
        jj += 1
    index=level_data != -2
    level_data = level_data*index
    #level_data=level_data[level_data != np.inf].reshape([-1, 24])
    index1=level_data!=np.inf
    index=index1*index
    level_data=np.nan_to_num(level_data)
    level_data2=level_data*index

    avg_level =(level_data2).sum(axis=0)/np.sum(index,axis=0)
    x = range(1, 25)
    plt.plot(x, avg_level,label=u"等级差为1以内",linewidth='2.0')
    csv_by_hour[:,3] = avg_level
    csv_by_hour[:,4]=avg_level-tmp_level
    plt.title(u'AQI等级差占比(%)')
    plt.xlabel(u'小时')
    xx = range(1, 25)
    plt.xticks(xx)
    plt.legend(loc='best')
    plt.grid(True)
    plt.savefig(u'所有站点等级差平均.png')
    plt.show()

def draw_level_avg2():
    level_data = np.zeros([1711, hour_num]) - 2
    jj = 0
    for ii in all_data2.values():
        kk = 0
        for iii in ii['data']['levels']:
            # if ii['data'][3][kk].get('0'): level_data[jj][kk]=-1;kk+=1;continue
            level_data[jj][kk] = ii['data']['levels'][kk][1]+ii['data']['levels'][kk][2]
            kk += 1
        jj += 1
    index=level_data != -2

    level_data = level_data*index

    #level_data=level_data[level_data != np.inf].reshape([-1, 24])
    index1=level_data!=np.inf
    index=index1*index
    level_data=np.nan_to_num(level_data)
    level_data2=level_data*index

    avg_level =(level_data2).sum(axis=0)/np.sum(index,axis=0)
    x = range(1, 25)
    plt.plot(x, avg_level,label=u"预测准确",linewidth='2.0')
    print avg_level
    summary_data[:, 2] = avg_level
    plt.title(u'AQI等级差占比(%)')
    plt.xlabel(u'小时')
    xx = range(1, 25)
    plt.xticks(xx)
    plt.grid(True)
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
    '''
    生成31个城市的逐日的预测mae和mse 前五列是mae,后五列是mse
    :return:
    '''
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
    tmp = np.zeros([31, 10])
    jj = 0
    for ii in city_data:
        print(ii)
        tmp[jj] = city_data[ii]['day_mae']  +city_data[ii]['day_mse']
        jj += 1
    for ii in range(capital_num):
        pass
    np.savetxt(u'省会城市的逐日数据.csv',tmp,fmt='%1.2f',delimiter=',')
    np.savetxt(u'所有站点的数据综合数据.csv',csv_by_hour,fmt='%1.3f',delimiter=',')
    return tmp
if __name__ == '__main__':
    calculate_avg_by_file();
    draw_city_mae()
    draw_city_mse()
    draw_level_avg()
    generate_csv()
