#coding:utf8
__author__ = 'cy'
from util import  connect
from matplotlib import  pyplot as plt

db=connect(host='54.223.178.198', port=27110)

c=db.compare_results

def  draw_mae(cities):
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
        mae=data['data'][0]
       # mae=map(lambda x:x)
        all_mae.append(mae)
        plt.plot(range(24),mae,label=ii)

    plt.legend()
    plt.title(u'mae')
    plt.xlabel(u'时间(小时)')
    plt.ylabel('mae')
    plt.show()
cities=['200'+str(ii)+'A' for ii in range(10)]
#draw_mae(cities)

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
       if ii==0:bars[ii] = plt.bar(x, all_data[ii],   linewidth=0, align='center',color=colors[ii] ,label='diff'+str(ii));
       else:
           #print add(all_data[:ii])
           bars[ii] = plt.bar(x, all_data[ii],   linewidth=0, align='center',bottom=add(all_data[:ii]),color=colors[ii],label='diff'+str(ii));
    plt.legend(loc='upper left')
    plt.show()
    return all_data


a=draw_level_dist('1001A')
