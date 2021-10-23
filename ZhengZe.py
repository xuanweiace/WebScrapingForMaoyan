#font = TTFont('22.woff')
#font.saveXML('22.xml')

import csv
import requests
from bs4 import BeautifulSoup
import re
class Maoyan():
    def __init__(self):
        self.header = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "Cache-Control": "max-age=0",
                        "Connection": "keep-alive",
                        "Cookie": "__mta=250379193.1530718965618.1552724185734.1552724186874.62; _"
                                  "lxsdk_cuid=16465f5cf2dc8-0994698fdc2ac7-16386950-fa000-16465f5cf2dc8; "
                                  "uuid_n_v=v1; uuid=7C57E28047C311E991B9E9D2BD010A06F94D2F7FE0214E68BD819AD9CE2300A3; _"
                                  "csrf=c2cda66b44c7a9967419cf9f1380acb41f32261f8158b5d047a141f9beefb3a3; _"
                                  "lxsdk=7C57E28047C311E991B9E9D2BD010A06F94D2F7FE0214E68BD819AD9CE2300A3; __"
                                  "mta=250379193.1530718965618.1552724158451.1552724183308.61; _"
                                  "lxsdk_s=1698590d4c2-02c-2b-16a%7C%7C45",
                        "Host": "maoyan.com",
                        "Referer": "https://maoyan.com/",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30"
                        }

        self.url = 'https://maoyan.com/board/4?offset='
        self.response = ''
        self.maoyan_dict = dict()
    def main(self):
        f = open('maoyan100.csv','w',newline='', encoding='utf-8-sig')
        csv_writer = csv.writer(f)
        csv_writer.writerow(["ID","详情页","Title","Name of actors","上映时间","Rating","Type","Duration","Name of actors","Cumulative income"])

        for i in range(0, 100, 10):
            print("正在爬取",i,"到",i+10)
            ret = self.get_one_page(str(i))
            for j in range(len(ret)):
                ret[j][6] = ','.join(ret[j][6])
                if ret[j][9] != '暂无':
                    ret[j][9] = ret[j][9] + '0000'
                csv_writer.writerow(ret[j])
        f.close()
        return ret 
    def requestOnce(self, url):
        return requests.get(url, headers = self.header)
    
    def normalize_overview(self, items):
        ret = []
        for o in items:
            ret.append([o[0],'https://maoyan.com'+o[1],o[2],o[3].strip(),o[4],o[5]+o[6]])
        return ret
    def get_one_page(self, offset):
        page_url = self.url + offset
        resp = self.requestOnce(page_url)
        #print(resp.status_code)
        #print(resp.text)
        pattern = re.compile(
        '<dd>.*?board-index.*?>(.*?)</i>.*?name.*?a.*?href="(.*?)".*?>(.*?)</a>.*?star.*?>(.*?)</p>.*?releasetime.*?>(.*?)</p>.*?integer.*?>(.*?)</i>.*?fraction.*?>(.*?)</i>',
        re.S)
        items = re.findall(pattern, resp.text)
        
        items = self.normalize_overview(items)
        for i in range(len(items)):
            items[i] += self.get_one_detail(items[i][1])
        return items
        
        
    def get_one_detail(self, url):
        resp = self.requestOnce(url)
        pattern1 = re.compile('<a class="text-link" href.*?>(.*?)<', re.S)
        type_list = re.findall(pattern1, resp.text)
        type_list = [item.strip() for item in type_list]
        #print(type_list)
        pattern2 = re.compile('class="ellipsis">.*?</li>.*?"ellipsis">.*?/(.*?)\n.*?</li>.*?class="ellipsis"', re.S)
        
        duration = re.findall(pattern2, resp.text)
        duration = duration[0].strip()
        #print(duration)
        
        pattern3 = re.compile('导演.*?class="name">(.*?)</a>', re.S)
        
        director = re.findall(pattern3, resp.text)
        director = director[0].strip()
        #print(director)
        
        pattern4 = re.compile('票房详情.*?film-mbox-item.*?film-mbox-item">.*?>(.*?)</div>', re.S)
        
        income = re.findall(pattern4, resp.text)
        if income == []:
            income = ["暂无"]
        income = income[0].strip()
        #print(income)
        
        return [type_list, duration, director, income]
        

ans = []
if __name__ == '__main__':
    my = Maoyan()
    ans = my.main()