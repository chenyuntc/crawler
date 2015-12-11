import os
import time

__author__ = 'cy'
#files = ['pm2_5201512100' + str(ii) for ii in range(1, 10)]
gaps = [1, 2, 3, 4, 5]
all_data = []
start_time='15-12-01'
end_time='15-12-10'



def get_files(start_time,end_time):
    '''

    :param start_time: 起始时间 格式如'15-12-01'
    :param end_time: 终止时间 格式同上
    :return: 所有需要处理的文件 ['pm2_5201512100','pm2_5201512101','pm2_5201512102'.....]
    '''
    '''
    根据 起始时间和终止时间获得所有要访问的文件
    start_time='15-12-01'
    end_time='15-12-10'-->[file1,file2.......]
    '''
    s_=start_time.split('-')
    start=int(time.strftime('%j',time.strptime(start_time,'%y-%m-%d')))
    end=int(time.strftime('%j',time.strptime(end_time,'%y-%m-%d')))
    all_files=[]
    for ii in range(start,end+1):
        tmp_time=time.strptime('15-%s' %ii,'%y-%j')
        tmp_day= time.strftime('%Y%m/%d/',tmp_time)
        tmp_day2=time.strftime('pm2_5%Y%m%d',tmp_time)
        h_24=['0'+str(ii) for ii in range(10)]+[str(ii) for ii in range(10,24)]
        b=[tmp_day+tmp_day2+(ii) for ii in h_24 ]
        all_files+=b
    return all_files;


def map_line(x):
    '''从文件的每一行读取有用信息'''
    res = x.split('  ')
    r0 = eval(res[0].split(' ')[-1])[1]
    r = [eval(ii)[1] for ii in res[1:]]
    return r

if __name__ == '__main__':
    files=get_files(start_time,end_time)
    for file in files:
            try:
                f=open('/home/cy/'+file)
                all_lines = f.readlines()
                all_info = map(map_line, all_lines)
                all_data.append(all_info)
            except Exception as e:
                print e
                all_data.append(-1)

            finally:
                f.close()

def calculate2(all_data, gaps):
    '''

    :param all_data: 所有的数据, 每一行代表着一个时间的数据,
    :param gaps: 所有要处理的间隔
    :return: 所有间隔
    '''
    results = []
    for gap in gaps:
        real_len=0
        result = 0
        for ii in range(len(all_data) - gap):
            if all_data[ii]==-1 or all_data[ii + gap]==-1:
                continue
            real_len+=1
            result += abs(all_data[ii][100][ gap] - all_data[ii + gap][100][0])
        results.append(float(result)/real_len)
    return results
