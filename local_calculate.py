#coding:utf8
__author__ = 'cy'
#from get_config import  mongo_host
mongo_host='54.223.178.198'

capital_num=31
# from get_config import  npz_path
# from get_config import  array_name

npz_path='./data-new.npz'
array_name='arr_0'
import  numpy as np
from util import connect



def get_capital_station():
    db=connect(host=mongo_host)
    collection=db.capital
    result=collection.find_one({'key':'capital_station'})
    data=result['data']
    return  data
capital_station_data=get_capital_station()
capitals=(capital_station_data.keys())
capitals_index={}
for ii in enumerate(capitals):
    capitals_index[ii[1]]=ii[0]

db=connect(host=mongo_host)
collection=db.capital
zone=collection.find_one({'key':'zone'})['data']
def load_data():
    data=np.load(npz_path)
    return  data[array_name]


def calculate_by_avg(capital_data):
    pass



def wrap(data,pre_day_num,useful_day_num):
    '''
    返回矩阵 每一列是提前1,2,3,4的预测值, 第一列是实测值;
    :param data:
    :return:result:第一维:城市31,第二维:实际时间,第三维:提前时间
    '''
    s=data.shape

    result=np.zeros([s[0],useful_day_num*24,pre_day_num])-np.nan
    true_data=data[:,-useful_day_num*24::,0]
    result[:,-24*useful_day_num::,0]=true_data
    #all_pre_data = data[:,useful_day_num*24-::24,3:27]
    for gap in xrange(1,pre_day_num):
        print gap
         ###########important a:b 不包括ｂ
        pre_gap_data=data[:,-3-(useful_day_num+gap-1)*24:-3-24*(gap-1):24,3+24*(gap-1):3+24*gap]
        result[:,:,gap]=pre_gap_data.reshape([31,-1])
    return  result


def get_data_of_mean():

        data=load_data()

        s=data.shape
        all_data=np.zeros([len(capital_station_data),s[0],s[2]])
        jj=0

        for ii in capital_station_data:

            int_station_codes=map(lambda x:int(x)-1001,capital_station_data[ii])
            capital_data=data[:,int_station_codes,:]
            capital_data[capital_data==-1]=np.nan
            mean_data=np.nanmean(capital_data,axis=1)
            all_data[jj,:,:]=mean_data
            jj+=1
        return all_data



if __name__ == '__main__':
    all_data=get_data_of_mean()
    pre_day_num=7;useful_day_num=7
    day_data=wrap(data=all_data,pre_day_num=7,useful_day_num=7)
    day_all_data=day_data.reshape([capital_num,-1,24,pre_day_num])
    day_mean=np.nanmean(day_all_data,axis=2)
    day_level=day_mean/50+1

    mae=np.nanmean(np.abs(day_mean-day_mean[:,:,0:1]),axis=1)
    mse=np.sqrt(np.nanmean((day_mean-day_mean[:,:,0:1])**2,axis=1))
    from matplotlib import  pyplot as plt
    width=1.0/(pre_day_num+2)
    color=['r','g','b','c','m','y','k','w']
    for city_index in range(capital_num ):
        for ii in range(pre_day_num):
            plt.bar(np.arange(useful_day_num)+width*ii,\
                    day_mean[city_index,:,ii],1.0/(pre_day_num+2),color=color[ii])
        plt.title(capitals[city_index])
        plt.savefig(capitals[city_index]+u'预测和实测的比较')
        plt.figure()
    #np.savetxt(u'实测和预测的比较')

    for every_zone in zone:
        for ii in zone[every_zone]:
            plt.plot(range(1,pre_day_num),mae[capitals_index[ii+u'市']][1:],lw=2,label=ii)
        plt.title(every_zone+u'逐日mae')
        plt.legend()
        plt.savefig(every_zone+u'逐日mae')
        plt.figure()
    mae_mse=np.hstack((mae,mse))
    np.savetxt(u'31个省会城市的逐日mae和mse.csv',mae_mse,fmt="%1.2f",delimiter=',')

    for every_zone in zone:
        for ii in zone[every_zone]:
            plt.plot(range(1,pre_day_num),mse[capitals_index[ii+u'市']][1:],lw=2,label=ii)
        plt.title(every_zone+u'逐日mse')
        plt.legend()
        plt.savefig(every_zone+u'逐日mse')
        plt.figure()


    day_level= np.floor(day_level)
    true_level_data=day_level[:,:,0:1]
    predict_data=day_level[:,:,1:]
    right_day=np.sum(np.abs(true_level_data-predict_data)<1,axis=1)


    np.savetxt(u'提前预测等级准确天数.csv',right_day,fmt='%1.1f',delimiter=',')
    for every_zone in zone:
        for ii,jj in zip(zone[every_zone],xrange(len(zone[every_zone] ))):
            #plt.plot(right_day[capitals_index[ii+u'市']][:],lw=2,label=ii)
            plt.bar(np.arange(len(right_day[capitals_index[ii+u'市']]))*width+jj,\
                    right_day[capitals_index[ii+u'市']] ,1.0/(pre_day_num+2),color=color[jj])
            plt.xticks(np.arange(0,len(zone[every_zone] ))+0.2,zone[every_zone])
        plt.title(every_zone+u'预报正确的天数')

        plt.ylabel(u'天数')

        plt.legend()
        plt.savefig(every_zone+u'预报正确的天数')
        plt.figure()
        day_level= np.floor(day_level)

    true_level_data=day_level[:,:,0:1]
    predict_data=day_level[:,:,1:]
    right_day=np.sum(np.abs(true_level_data-predict_data)<2,axis=1)


    np.savetxt(u'提前预测等级相差1以内.csv',right_day,fmt='%1.1f',delimiter=',')
    for every_zone in zone:
        for ii,jj in zip(zone[every_zone],xrange(len(zone[every_zone] ))):
            #plt.plot(right_day[capitals_index[ii+u'市']][:],lw=2,label=ii)
            plt.bar(np.arange(len(right_day[capitals_index[ii+u'市']]))*width+jj,\
                    right_day[capitals_index[ii+u'市']] ,1.0/(pre_day_num+2),color=color[jj])
            plt.xticks(np.arange(0,len(zone[every_zone] ))+0.2,zone[every_zone])
        plt.title(every_zone+u'预报相差为1以内的天数')

        plt.ylabel(u'天数')

        plt.legend()
        plt.savefig(every_zone+u'预报等级相差1以内的天数')
        plt.figure()













