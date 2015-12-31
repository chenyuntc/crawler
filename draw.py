#coding:utf8
__author__ = 'cy'
capital_num,day_num=31,7
from util import  connect
from matplotlib import  pyplot as plt
import  numpy as np
summary_data=np.zeros([24,10])

db=connect(host='54.223.178.198', port=27110)

c=db.compare_results
station_num=1496
hour_num=24

#all_data=[]
#for ii in c.find({'key':'compare_results','end_time':'15-11-08'}):
  #  all_data.append(ii)


all_data2={}
for ii in c.find({'key':'compare_results','end_time':'15-12-30'}):
    all_data2[ii['city']]=(ii)
all_data=all_data2

capital=db.capital
cities=capital.find_one({'key':'capital'})
x_ticks=[ii[0] for ii in cities['data']]
capital_data={}
for ii in cities['data']:
    capital_data[ii[0]]=all_data2[ii[4]]


zone=capital.find_one({'key':'zone'})


def  draw_mae(cities,start_time=None,end_time=None):
    '''
获取城市列表中各个城市的mae谁时间的变化
    :param cities: list, ['2001A','2002A'...]
    :param start_time 计算数据的起始时间
    :param end_time 计算的终止时间
    :return: None
    '''
    x=range(24)
    all_mae=[]
    for ii in cities:
        data=c.find_one({'city':ii})
        if not data:continue
        mae=data['data'][0]
       # mae=map(lambda x:x)
        all_mae.append(mae)
        plt.plot(range(24),mae,label=ii)

    plt.legend(loc='upper left')
    plt.title(u'mae of different cities')
    plt.xlabel(u'time(h)')
    plt.ylabel('mae')
    plt.show()

def  draw_mse(cities):
    '''
    获取城市列表中各个城市的mae谁时间的变化
    :param cities: list, ['2001A','2002A'...]
    :return: None
    '''
    x=range(24)
    all_mae=[]
    for ii in cities:
        data=c.find_one({'city':ii})
        if not data:continue
        mse=data['data'][1]
       # mae=map(lambda x:x)
        all_mae.append(mse)
        plt.plot(range(24),mse,label=ii)

    plt.legend(loc='upper left')
    plt.title(u'mae of different cities')
    plt.xlabel(u'time(h)')
    plt.ylabel('mae')
    plt.show()



def  draw_day_mse(cities):
    '''
获取城市列表中各个城市的mae谁时间的变化
    :param cities: list, ['2001A','2002A'...]
    :return: None
    '''
    x=range(24)
    all_mae=[]
    for ii in cities:
        data=c.find_one({'city':ii})
        if not data:continue
        mse=data['data'][2][0]
       # mae=map(lambda x:x)
        all_mae.append(mse)
        plt.plot(range(24),mse,label=ii)

    plt.legend(loc='upper left')
    plt.title(u'mae of different cities')
    plt.xlabel(u'time(h)')
    plt.ylabel('mae')
    plt.show()

cities=['200'+str(ii)+'A' for ii in range(10)]


def draw_sqrt(city):
    '''
获取城市列表中各个城市的mae谁时间的变化
    :param cities: list, ['2001A','2002A'...]
    :return: None
    '''
    x=range(24)
    all_mae=[]
    for ii in cities:
        data=c.find_one({'city':ii})
        if not data:continue
        mse=data['data'][2][0]
       # mae=map(lambda x:x)
        all_mae.append(mse)
        plt.plot(range(24),mse,label=ii)

    plt.legend(loc='upper left')
    plt.title(u'mae of different cities')
    plt.xlabel(u'time(h)')
    plt.ylabel('mae')
    plt.show()


def add(l):

    ll=len(l[0])
    result=[0 for jjj in range(ll)]
    for ii in range(ll):
        for jj in l:
            result[ii]+=jj[ii]

    return  result

def draw_level_dist(city):
    x=range(24)
    bars=range(5)
    colors=['r','y','g','b','k']

    all_data=[list() for i2121 in range(5)]
    data=c.find_one({'city':city})
    if not data: raise Exception('not find city data')
    level=data['data'][3]
    for ii in range(5):
       for jj in level:
           all_data[ii].append(jj.get(str(ii),0))
       if ii==0:bars[ii] = plt.bar(x, all_data[ii],   linewidth=0, align='center',color=colors[ii]\
                                   ,label='diff'+str(ii));
       else:
           #print add(all_data[:ii])
           bars[ii] = plt.bar(x, all_data[ii],   linewidth=0, align='center'\
                              ,bottom=add(all_data[:ii]),color=colors[ii],label='diff'+str(ii));
    plt.legend(loc='upper left')
    plt.show()
    return all_data


#a=draw_level_dist('1001A')

def float_range(start,stop,step):
    i=start
    if start>stop:raise Exception('start >stop error')
    while i<stop:
        yield  i
        i+=step

def draw_avg():
    '''
    计算1500个站点所有的mae和mse
    :return:
    '''
    a=np.ones([station_num, hour_num])
    jj=0
    for ii in all_data2.values():
        a[jj]=ii['data'][0]
        jj+=1
    a=np.array(filter(lambda  x: (x[0]+1)*x[0]!=0, a))
    avg=a.mean(axis=0)
    print avg
    summary_data[:,0]=avg
    x=range(1,25)
    plt.plot(x,avg,label='MAE')
    plt.title(u"所有站点 AQI数值MAE和mse")
    plt.xlabel(u"小时")
    plt.grid(True)
    a=np.ones([station_num, hour_num])
    jj=0
    for ii in all_data2.values():
        a[jj]=ii['data'][1]
        jj+=1
    a=a[a!=-1].reshape([-1,24])
    avg=a.mean(axis=0)
    summary_data[:,1]=avg
    plt.plot(x,avg,label='MSE')
    print avg
    xx=range(1,25)
    plt.xticks(xx)



    plt.title(u"所有站点 AQI数值MSE")
    plt.xlabel(u"小时")
    plt.grid(True)
    plt.xticks(xx)
    plt.legend(loc='best')
    plt.show()

def draw_level_avg():
    level_data=np.zeros([station_num,hour_num])-2
    jj=0
    for ii in all_data.values():
        kk=0
        for iii in ii['data'][3]:
           # if ii['data'][3][kk].get('0'): level_data[jj][kk]=-1;kk+=1;continue
            level_data[jj][kk]=ii['data'][3][kk].get('0',0)
            kk+=1
        jj+=1

    level_data=level_data[level_data!=-2].reshape([-1,24])
    avg_level=level_data.mean(axis=0)
    x=range(1,25)
    plt.plot(x,avg_level)
    print avg_level
    summary_data[:,2]=avg_level
    plt.title(u'AQI等级差为0(%)')
    plt.xlabel(u'小时')
    xx=range(1,25)
    plt.xticks(xx)
    plt.grid(True)
    plt.show()



def draw_level_avg_2():
    level_data=np.zeros([station_num,hour_num])-2
    jj=0
    for ii in all_data.values():
        kk=0
        for iii in ii['data'][3]:
           # if ii['data'][3][kk].get('0'): level_data[jj][kk]=-1;kk+=1;continue
            level_data[jj][kk]=ii['data'][3][kk].get('0',0)+ii['data'][3][kk].get('1',0)
            kk+=1
        jj+=1
    level_data=level_data[level_data!=-2].reshape([-1,24])
    avg_level=level_data.mean(axis=0)
    x=range(1,25)
    plt.plot(x,avg_level)
    print avg_level
    summary_data[:,9]=avg_level
    plt.title(u'AQI等级差为0,1(%)')
    plt.xlabel(u'小时')
    plt.grid(True)
    xx=range(1,25)
    plt.xticks(xx)
    plt.show()

def draw_city_mse():
    '''
    话所有城市的mse 柱状图 总共话7张或者9张 ,每张包含31个城市的mse
    :return:
    '''
    city_mae=np.zeros([capital_num,day_num])
    jj=0
    new_x_ticks=[ii[:-1] for ii in x_ticks]
    for ii in x_ticks:

        city_mae[jj]=capital_data[ii]['data'][2][1][:day_num]
        jj+=1
    for ii in range(day_num):
        plt.bar(range(1,capital_num+1),city_mae[:,ii])
        plt.xticks(np.linspace(1.5,capital_num+0.5,capital_num ),new_x_ticks)
        plt.show()



def draw_city_mse():
    '''
    话所有城市的mae 柱状图 总共话7张或者9张 ,每张包含31个城市的mae
    :return:
    '''
    city_mae=np.zeros([capital_num,day_num])
    zone_mae={}
    jj=0
    new_x_ticks=[ii[:-1] for ii in x_ticks]
    for ii in x_ticks:

        city_mae[jj]=capital_data[ii]['data'][2][1][:day_num]
        jj+=1
    # for ii in range(capital_num):
    #     plt.plot(range(1,day_num+1),city_mae[ii,:],label=x_ticks[ii])
    #     if (ii!=0 and  ii%5==0) or ii==capital_num-1:
    #         plt.legend(loc='best')
    #         plt.show()

    for  every_zone in zone['data']:
        max_num=[]
        for every_city in zone['data'][every_zone]:

            plt.plot(np.arange(1,day_num+1) ,capital_data[every_city+u'市']['data'][2][1][:day_num],'-o',\
                     label=every_city, linewidth='2.0')
            max_num.append(max(capital_data[every_city+u'市']['data'][2][1][:day_num] ))
        plt.title(every_zone+u'地区7天预测MSE')
        plt.legend(loc='best')
        plt.xlabel(u'提前天数')
        plt.ylim([0,max(max_num)*1.1])
        plt.grid(True)
        plt.savefig(u'mse_'+unicode(every_zone))

        plt.show()
def draw_city_mae():
    '''
    话所有城市的mae 柱状图 总共话7张或者9张 ,每张包含31个城市的mae
    :return:
    '''
    city_mae=np.zeros([capital_num,day_num])
    zone_mae={}
    jj=0
    new_x_ticks=[ii[:-1] for ii in x_ticks]
    for ii in x_ticks:

        city_mae[jj]=capital_data[ii]['data'][2][0][:day_num]
        jj+=1
    # for ii in range(capital_num):
    #     plt.plot(range(1,day_num+1),city_mae[ii,:],label=x_ticks[ii])
    #     if (ii!=0 and  ii%5==0) or ii==capital_num-1:
    #         plt.legend(loc='best')
    #         plt.show()

    for  every_zone in zone['data']:
        max_num=[]
        for every_city in zone['data'][every_zone]:

            plt.plot(np.arange(1,day_num+1) ,capital_data[every_city+u'市']['data'][2][0][:day_num],'-o',\
                     label=every_city, linewidth='2.0')
            max_num.append(max(capital_data[every_city+u'市']['data'][2][0][:day_num] ))
        plt.title(every_zone+u'地区7天预测mae')
        plt.legend(loc='best')
        plt.xlabel(u'提前天数')
        plt.ylim([0,max(max_num)*1.1])
        plt.grid(True)
        plt.savefig(u''+unicode(every_zone))

        plt.show()


def generate_csv():
    city_mae=np.zeros([capital_num,day_num])
    city_data={}
    zone_mae={}
    jj=0
    f=open('city_data.csv','w' )
    new_x_ticks=[ii[:-1] for ii in x_ticks]
    for ii in x_ticks:

       # city_mae[jj]=capital_data[ii]['data'][2][0][:day_num]
        city_data[ii]=capital_data[ii]['data']
        jj+=1
    tmp=np.zeros([31,18])
    jj=0
    for ii in city_data:
        print(ii)
        tmp[jj]=city_data[ii][2][0]+city_data[ii][2][1]
        jj+=1
    for ii in range(capital_num):
        pass
        #plt.plot(range(1,day_num+1),city_mae[ii,:],label=x_ticks[ii])
        #if (ii!=0 and  ii%5==0) or ii==capital_num-1:
          #  plt.legend(loc='best')
            #plt.show()
