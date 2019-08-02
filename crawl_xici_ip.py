# -*- coding: utf-8 -*-


__author__ = 'bobby'
import requests
from scrapy.selector import Selector
import MySQLdb
import random

db_name = 'article_spider'
# mysql_table_name = 'proxy_ip'
mysql_table_name = 'proxy_ip_3366'

conn = MySQLdb.connect(host="192.168.137.253", user="root", passwd="123", db=db_name, charset="utf8")
cursor = conn.cursor()


def crawl_ips():
    #爬取西刺的免费ip代理


    some_user_agent_list = ["Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36",
     "Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
     "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36",
     "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
     "Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17",
     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17",
     "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15",
     "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14",
     "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16"]
    random_index = random.randint(0, len(some_user_agent_list) - 1)
    random_agent = some_user_agent_list[random_index]

    headers = {"User-Agent":random_agent}
    # headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"}
    for i in range(200,201):
    # for i in range(100,3761):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)

        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")


        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            all_texts = tr.css("td::text").extract()

            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]

            ip_list.append((ip, port, proxy_type, speed))

        for ip_info in ip_list:
            cursor.execute(
                "insert ignore into {0}(ip, port, speed, proxy_type) VALUES('{1}', '{2}', {3}, 'HTTP')".format(
                    mysql_table_name, ip_info[0], ip_info[1], ip_info[3]
                )
            )

            conn.commit()


class GetIP(object):
    def delete_ip(self, ip):
        #从数据库中删除无效的ip
        delete_sql = """
            delete from {0} where ip='{1}'
        """.format(mysql_table_name, ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        #判断ip是否可用
        http_url = "http://epub.sipo.gov.cn/"
        # http_url = "http://www.zhidaxue.com/"
        # http_url = "https://www.zhihu.com/signin?next=%2F"
        # http_url = "http://www.baidu.com"
        # http_url = "http://www.wanfangdata.com.cn/details/detail.do?_type=patent&id=US201715732509"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http":proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            # print ("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                # print ("effective ip")
                return True
            else:
                # print  ("invalid ip and port")
                self.delete_ip(ip)
                return False


    def get_random_ip(self):
        #从数据库中随机获取一个可用的ip
        random_sql = """
              SELECT ip, port FROM {0}
            ORDER BY RAND()
            LIMIT 1
            """.format(mysql_table_name)
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]

            judge_re = self.judge_ip(ip, port)
            if judge_re:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()



def main():
    # print(crawl_ips())
    get_ip = GetIP()
    for i in range(50):
        print(get_ip.get_random_ip())
    # get_ip = GetIP()
    # for i in range(10):
    #     print(get_ip.get_random_ip())
    # effect_ip_list = []
    # for item in range(1, 5000):
    #     try:
    #         effect_ip = get_ip.get_random_ip()
    #         print(effect_ip)
    #         effect_ip_list.append(effect_ip)
    #     except:
    #         break
    # print(effect_ip_list)



# print (crawl_ips())
if __name__ == "__main__":
    main()

    effective_ip_list = ["http://118.178.148.126:80", "http://121.233.251.225:9999", "http://182.35.83.39:9999", "http://61.189.242.243:55484",
    "http://113.121.21.181:9999", "http://220.173.103.46:8082", "http://182.35.81.185:9999", "http://171.13.102.94:9999",
    "http://60.169.115.253:808", "http://118.178.148.126:80", "http://60.205.229.126:80", "http://1.197.16.74:9999", "http://182.35.82.127:9999",
    "http://1.197.203.94:9999", "http://120.79.147.254:9000", "http://113.121.22.168:9999", "http://123.163.97.238:9999", "http://1.197.203.97:9999",
    "http://106.75.8.141:808", "http://1.197.203.62:9999"]
