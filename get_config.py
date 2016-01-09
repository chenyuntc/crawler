#coding:utf8
from ConfigParser import ConfigParser
import pymongo
from util import get_files

__author__ = 'cy'
cf = ConfigParser()
cf.read('dev.cfg')
city_num = int(cf.get('calculate', 'city_num'))
predict_hour = int(cf.get('calculate', 'predict_hour'))
file_path = cf.get('file', 'filepath')
start_time = cf.get('file', 'start_time')
end_time = cf.get('file', 'end_time')
gaps = eval(cf.get('calculate', 'gaps'))
all_files = (get_files(start_time, end_time))
day_gaps=eval(cf.get('calculate','day_gaps'))
mongo_host=cf.get('mongodb','host')
mongo_port=int(cf.get('mongodb','port'))
mongo_db_name=cf.get('mongodb','db_name')
client=pymongo.MongoClient(mongo_host,mongo_port)
db=client.get_database(mongo_db_name)
bins = eval(cf.get('calculate', 'bins'))
collection_name=cf.get('mongodb','collection')