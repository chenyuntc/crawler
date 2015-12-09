#coding;utf8
#from bs4 import  BeautifulSoup
from urllib2 import  urlopen
import pymongo
import time
to_scrapy={'/300'}
d1=set()
d2=set()


'''def get_url(url):
    r=urlopen(url)
    ids=set()
    res=BeautifulSoup(r.read())
    b=res.find_all('div','list')
    all_ids=b[0].find_all()
    for ii in all_ids[1::2]:
    	t=ii.findChild()
        print t.get_text()
    	ids.add(str(t.get('href')))
    return ids
'''

def get_data(url,finfo,db,t):
    info=urlopen(url)
    b=info.read()
    if b=='':
        return
    finfo.write(str(b.decode('unicode-escape').encode('utf8')+'\n'))
    finfo.flush()
    db[str(int(t))].insert_one( eval(b.decode('unicode-escape'))  )


'''while len(to_scrapy)>0:
    url =to_scrapy.pop()
    if url not in d1:
    	try:
            ids=get_url('http://pm25.moji.com/'+url)
        except Exception as e:
            print e
        d1.add(url)
    	to_scrapy=to_scrapy.union(ids-d2)
    	for ii in ids:
    		get_data('http://pm25.moji.com/highchart'+ii)
    		d2.add(ii)'''

if __name__ == '__main__':
    finfo=open('info2.txt','w')
    client=pymongo.MongoClient('54.223.178.198',27110)
    db=client.test
    t=time.time()
    for ii in range(1,3005):
       get_data('http://pm25.moji.com/highchart/'+str(ii),finfo,db,t)

    finfo.close()
    client.close()





        