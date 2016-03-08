#coding:utf8
__author__ = 'cy'
#from get_config import  mongo_host
mongo_host='54.223.178.198'

capital_num=31
# from get_config import  npz_path
# from get_config import  array_name

npz_path='./new_data.npz'
array_name='new_data'
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
    返回矩阵 每一列是提前1,2,3,4小时的预测值, 第一列是实测值;
    :param data:输入data的（ (31, 336, 241)） 336那个维度  最后部分数据必须是需要评测的数据（比如168: 评估的是对这七天的预测能力）
    :return:result:  (31, 168, 7)  第一维:城市31,第二维:实际时间（小时）,第三维:提前时间（天）
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


        '''
        mean是这个城市所有站点的mean，数据依旧是逐小时的
    :return:
    '''
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


def cal_per_less50(data):
    '''
    计算小于50的比例
    :param data: (31, 336, 241)
    :return:all_result:   (31,120) 31个城市，120个提前小时预测错误的比例
    '''
    s=data.shape
    all_result=np.zeros([s[0],24*5])
    for hour_gap in xrange(1,24*5+1):
        true_data=data[:,hour_gap:,0]
        predict_data=data[:,:-hour_gap,hour_gap]
        diff=predict_data-true_data
        # avg=np.nanmean(diff,axis=1)
        valid_data_num=np.sum(~np.isnan(diff),axis=1)
        predict_wrong=np.abs(diff)>50
        predict_wrong_num=np.sum(predict_wrong,axis=1,dtype=np.float)
        all_result[:,hour_gap-1]=(predict_wrong_num/valid_data_num)
    return all_result

if __name__ == '__main__':
    all_data=get_data_of_mean()#31个城市逐小时预测未来240个小时的数据(31, 336, 241)
    pre_day_num=7;useful_day_num=16

    #31个城市逐天晚上九点实测和预测（预测和实测均是逐小时）(31, 168, 7)
    day_data=wrap(data=all_data,pre_day_num=pre_day_num,useful_day_num=useful_day_num)
    day_all_data=day_data.reshape([capital_num,-1,24,pre_day_num])
    day_mean=np.nanmean(day_all_data,axis=2)# (31, 7, 7)

    day_level=day_mean/50+1

    mae=np.nanmean(np.abs(day_mean-day_mean[:,:,0:1]),axis=1)
    mse=np.sqrt(np.nanmean((day_mean-day_mean[:,:,0:1])**2,axis=1))
    from matplotlib import  pyplot as plt
    width=1.0/(pre_day_num+2)
    color=['r','g','b','c','m','y','k','w']
    labels=[u'实测AQI']+[u'提前%s天预测值' %jjj for jjj in range(1,pre_day_num)]
    for city_index in range(capital_num ):
        for ii in range(pre_day_num):
            #important 7是除夕
            plt.bar(np.arange(useful_day_num)+7+width*ii,\
                    day_mean[city_index,:,ii],1.0/(pre_day_num+2),color=color[ii],label=labels[ii])
        plt.title(capitals[city_index])
        plt.xlabel(u'二月(日期)')
        plt.ylabel(u'aqi')
        plt.legend(ncol=2)
        plt.savefig(capitals[city_index]+u'预测和实测的比较')
        plt.figure()
    #np.savetxt(u'实测和预测的比较')

    for every_zone in zone:
        for ii in zone[every_zone]:
            plt.plot(range(1,pre_day_num),mae[capitals_index[ii+u'市']][1:],lw=2,label=ii)
        plt.title(every_zone+u'逐日mae')
        plt.xlabel(u'提前预测时间(天)')
        plt.legend(loc=0)
        plt.ylabel(u'mae')
        plt.savefig(every_zone+u'逐日mae')
        plt.figure()
    mae_mse=np.hstack((mae,mse))
    np.savetxt(u'31个省会城市的逐日mae和mse.csv',mae_mse,fmt="%1.2f",delimiter=',')

    for every_zone in zone:
        for ii in zone[every_zone]:
            plt.plot(range(1,pre_day_num),mse[capitals_index[ii+u'市']][1:],lw=2,label=ii)
        plt.title(every_zone+u'逐日mse')
        plt.xlabel(u'提前预测时间(天)')
        plt.legend(loc=0)
        plt.ylabel(u'mse')
        plt.savefig(every_zone+u'逐日mse')
        plt.figure()


    day_level= np.floor(day_level)
    true_level_data=day_level[:,:,0:1]
    predict_data=day_level[:,:,1:]
    right_day=np.sum(np.abs(true_level_data-predict_data)<1,axis=1)/16.0


    np.savetxt(u'提前预测等级准确比例.csv',right_day,fmt='%1.2f',delimiter=',')
    for every_zone in zone:
        for ii,jj in zip(zone[every_zone],xrange(len(zone[every_zone] ))):
            #plt.plot(right_day[capitals_index[ii+u'市']][:],lw=2,label=ii)
            plt.bar(np.arange(len(right_day[capitals_index[ii+u'市']]))*width+jj,\
                    right_day[capitals_index[ii+u'市']] ,1.0/(pre_day_num+2),color=color[jj])
            plt.xticks(np.arange(0,len(zone[every_zone] ))+0.2,zone[every_zone])
        plt.title(every_zone+u'地区预报正确的比例')

        plt.ylabel(u'比例')
        plt.ylim([0,0.9])

        plt.legend(loc=0)
        plt.savefig(every_zone+u'预报正确的比例')
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

        plt.legend(loc=0)
        plt.savefig(every_zone+u'预报等级相差1以内的天数')
        plt.figure()




    all_result=cal_per_less50(all_data)
    for every_zone in zone:
        for ii,jj in zip(zone[every_zone],xrange(len(zone[every_zone] ))):
            plt.plot(1-all_result[capitals_index[ii+u'市']][:],lw=2,label=ii)
        plt.title(every_zone+u'预报相差小于50以内的比例')

        plt.ylabel(u'比例')
        plt.xlabel(u'提前时间(小时)')

        plt.legend(loc=0)
        plt.savefig(every_zone+u'预报相差小于50以内的比例')

        plt.figure()


    #
    # for every_zone in zone:
    #     for ii,jj in zip(zone[every_zone],xrange(len(zone[every_zone] ))):
    #         plt.plot(1+np.arange(696)/24.0,all_data2[capitals_index[ii+u'市']][:],lw=1,label=ii)
    #         print ii,jj
    #     plt.title(every_zone+u'实测AQI')
    #
    #     plt.ylabel(u'AQI大小')
    #     plt.xlabel(u'日期')
    #
    #     plt.legend(loc=0)
    #     plt.savefig(every_zone+u'实测AQI')
    #
    #     plt.figure()
    #







