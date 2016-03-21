#coding:utf8
#from bs4 import  BeautifulSoup
from urllib2 import  urlopen
import pymongo
import time

def get_data(url,db,t):
    b=urlopen(url).read()
    if b=='':
        return
    db['moji_data'].insert_one(\
        { 'data':eval(b.decode('unicode-escape')),\
          'key':'moji',
          'time':t})

if __name__ == '__main__':
    client=pymongo.MongoClient('54.223.178.198',27110)#'172.31.11.244'
    db=client.test
    ids=db['city_id'].find_one({'key':'all_id'})['data']
    t=time.strftime('20%y-%m-%d %H:%M')
    c=db['moji_data']
    c.remove()
    for ii in ids:
       try:
           get_data('http://pm25.moji.com/highchart/'+str(ii),db,t)
       except Exception  as e:
          print e
          print ii
    client.close()






