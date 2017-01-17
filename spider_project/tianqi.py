#-*-encoding:utf-8-*-
import requests
from bs4 import BeautifulSoup
import time
import datetime
import pymongo
import pprint


#
# def id_get(word):
#     t = int(time.time())
#     url = 'http://toy1.weather.com.cn/search?cityname=' + urllib.quote(word) + '&callback=success_jsonpCallback&_=' + str(t)
#     print url
#     header = {
#     'Host': 'toy1.weather.com.cn',
#     'Connection': 'keep-alive',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
#     'Accept': '*/*',
#     'Referer': 'http://www.weather.com.cn/weather1d/101190101.shtml',
#     'Accept-Encoding': 'gzip, deflate, sdch',
#     'Accept-Language': 'zh-CN,zh;q=0.8'
#     }
#     r = requests.get(url,headers=header)
#     con = eval(r.content.split("jsonpCallback(")[1].strip()[:-1])
#     id = ''
#     for c in con:
#         c = c["ref"].split(r'~')
#         if word in c:
#             id = c[0]
#             break
#     return id

#明日天气
def tomorrow_weather(id):
    url = 'http://www.weather.com.cn/weather/' + str(id) + '.shtml'
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'lxml')
    weather_tomorrow = soup.select("#7d > ul > li")[1]
    w_date = weather_tomorrow.select("h1")[0].get_text().strip()
    w_wea = weather_tomorrow.select(".wea")[0].get_text().strip()
    w_tem = weather_tomorrow.select(".tem")[0].get_text().strip()
    w_all = w_date + u',天气' + w_wea + u",气温" + w_tem + u"。"
    return w_all.encode("utf8")

def weather_get(id):
    t = int(time.time())
    #实时天气url
    url = 'http://d1.weather.com.cn/sk_2d/'+ str(id) + '.html?_=' + str(t)
    print url
    #各类指数url
    url_index = 'http://www.weather.com.cn/weather1d/' + str(id)  + '.shtml'
    print url_index
    header = {
    'Host': 'd1.weather.com.cn',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'http://www.weather.com.cn/weather1d/101190101.shtml',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    header_index = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
     'Accept-Encoding': 'gzip, deflate, sdch',
     'Accept-Language': 'zh-CN,zh;q=0.8',
     'Cache-Control': 'max-age=0',
     'Connection': 'keep-alive',
     'Host': 'www.weather.com.cn',
     'Referer': 'http://www.weather.com.cn/weather/101280601.shtml',
     'Upgrade-Insecure-Requests': '1',
     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
    r = requests.get(url,headers=header,timeout=6)
    data = eval(r.content.split("dataSK =")[1].strip())
    r_index = requests.get(url_index,headers=header_index,timeout=6)
    # print r_index.content
    tomorrow_wea = tomorrow_weather(id)
    data_index_w = BeautifulSoup(r_index.content,"lxml").select(".livezs > ul > li")
    d1 = data_index_w[0].em.get_text() + u":" + data_index_w[0].span.get_text() + u',' + data_index_w[0].p.get_text()
    d2 = data_index_w[1].em.get_text() + u":" + data_index_w[1].span.get_text() + u',' + data_index_w[1].p.get_text()
    d3 = data_index_w[4].em.get_text() + u":" + data_index_w[4].span.get_text() + u',' + data_index_w[4].p.get_text()
    d4 = data_index_w[5].em.get_text() + u":" + data_index_w[5].span.get_text() + u',' + data_index_w[5].p.get_text()
    result_data = data["cityname"].decode("utf8") + u"," + data["date"].decode("utf8") + u",天气" + data["weather"].decode("utf8")+ u',当前气温' + \
                  data["temp"].decode("utf8") + u"°C，" + data["WD"].decode("utf8") + \
                  data["WS"].decode("utf8") + u",相对湿度" + data["SD"] + u'。' + d1 + d2 + d3 + d4 + tomorrow_wea.decode("utf8")
    hour = str(datetime.datetime.now()).split(":")[0].split(" ")[1]
    update_time = str(datetime.datetime.now()).split(".")[0]
    result_dict ={"city_id":str(id),
                  "city":data["cityname"],
                  "date":data["date"],
                  "weather":data["weather"],
                  "temperature":data["temp"],
                  "wind": data["WD"].decode("utf8") + data["WS"].decode("utf8"),
                  "humidity":data["SD"],
                  "uv_index":d1.encode("utf8"),
                  "cold_index":d2.encode("utf8"),
                  "motion_index":d3.encode("utf8"),
                  "air_index":d4.encode("utf8"),
                  "weather_all":result_data.encode("utf8"),
                  "tomorrow_wea":tomorrow_wea,
                  "hour":hour,
                  "update_time":update_time}
    # pprint.pprint(result_dict)
    return result_dict

def city_get():
    f = open("city_id.txt",'r')
    # f = open("city_id.txt",'r')
    ff = f.readlines()
    d = []
    for i in ff:
        d.append(i.strip())
    f.close()
    return d

def mongo_insert(id,weather_dict):
    conn = pymongo.MongoClient("192.168.10.219",49019)
    conn["hhly"]["weather"].update({"city_id":id},weather_dict,True)
    print id + "-" +weather_dict["city"] + ": insert success"
    conn.close()


def epool_spider(i):
    try:
        weather_dict = weather_get(i)
        mongo_insert(i,weather_dict)
    except Exception,e:
        t =  str(datetime.datetime.now()).split(".")[0]
        print Exception,e
        f = open("weather_lose.txt",'a+')
        # f = open("weather_lose.txt",'a+')
        f.write(t + " " + i+ str(Exception) + str(e) + '\n')
        f.close()


def main():
    city_list = city_get()
    for i in city_list:
        time.sleep(1)
        epool_spider(i)


if __name__ == "__main__":
    main()
