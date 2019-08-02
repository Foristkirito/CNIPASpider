# -*- coding: utf-8 -*-
# 开发团队   ：CSSC_linyuanlab
# 开发人员   ：yyc
# 开发时间   ：2019/7/11  17:27
# 文件名称   ：selenium_spider_CNIPA.py
# 开发工具   ：PyCharm
import random

from selenium import webdriver
import time
import datetime
import os
import sys
import MySQLdb
import MySQLdb.cursors
from selenium import webdriver
from crawl_xici_ip import GetIP


import logging

"""爬虫控制"""
"""爬取第一类专利：发明公布"""
data_index = 0
start_page = 1
end_page = 2000
data_name_patent = ['CN_patent_invention_published','CN_patent_invention_authorized',
                    'CN_patent_utility_new','CN_patent_appearance_designed']
data_label_patent = ['发明公布', '发明授权', '实用新型', '外观设计']
# 确定数据集的位置
data_type_patent = [1,2,3,4]

logger = logging.getLogger(data_name_patent[data_index])  # 定义对应的程序模块名name，默认是root
logger.setLevel(logging.INFO)  # 指定最低的日志级别 critical > error > warning > info > debug

consol_haddler = logging.StreamHandler()  # 日志输出到屏幕控制台
consol_haddler.setLevel(logging.INFO)  # 设置日志等级

#  这里进行判断，如果logger.handlers列表为空，则添加，否则，直接去写日志，解决重复打印的问题
if not logger.handlers:
    file_haddler = logging.FileHandler(data_name_patent[data_index]+'.log', encoding = "utf-8")  # 向文件log.txt输出日志信息，encoding="utf-8",防止输出log文件中文乱码
    file_haddler.setLevel(logging.INFO)  # 设置输出到文件最低日志级别

    formatter = logging.Formatter("%(asctime)s %(name)s- %(levelname)s - %(message)s")
    # %(asctime)s	字符串形式的当前时间。默认格式是 “2003-07-08 16:49:45,896”。逗号后面的是毫秒
    # %(name)s 自定义的模块名

    consol_haddler.setFormatter(formatter)  # 选择一个输出格式，可以定义多个输出格式
    file_haddler.setFormatter(formatter)

    logger.addHandler(file_haddler)  # 增加指定的handler
    logger.addHandler(consol_haddler)


project_path = os.path.abspath(os.path.dirname(sys.argv[0]))
field_name_list = ['name', 'announcement_id', 'announcement_date', 'filing_id', 'filing_date',
                   'patentee', 'designer', 'address', 'IPC']




def setup():
    # CNIPA_conn = MySQLdb.connect('192.168.0.101', 'root', 'root', 'cnipa', charset="utf8", use_unicode=True)
    CNIPA_conn = MySQLdb.connect('192.168.137.253', 'root', '123', 'cnipa', charset="utf8", use_unicode=True)
    CNIPA_cursor = CNIPA_conn.cursor()
    insert_sql = """
        insert ignore into {0}({1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9})
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """.format(data_name_patent[data_index], field_name_list[0], field_name_list[1], field_name_list[2], field_name_list[3],
               field_name_list[4], field_name_list[5], field_name_list[6], field_name_list[7], field_name_list[8])


    # _____________________基本设定___________________________
    FIREFOX_DRIVER_PATH = project_path + '\\enforcement\\geckodriver.exe'
    # # 设置代理
    # PROXY_list = ["http://122.234.171.146:8060", "http://123.115.130.41:8060", "http://119.51.145.56:8080",
    #  "http://118.250.3.13:8060", "http://122.141.114.67:8080", "http://180.109.165.80:8118",
    #  "http://112.74.106.205:80", "http://116.231.231.176:8060", "http://112.74.106.205:80",
    #  "http://119.134.110.12:8118"]

    # _____________________启动参数___________________________
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--start-maximized')

    get_ip = GetIP()
    for item in range(100):
        PROXY = get_ip.get_random_ip()
        try:
            firefox_options.add_argument("--proxy-server={0}".format(PROXY))

            # _____________________启动浏览器___________________________
            browser = webdriver.Firefox(executable_path=FIREFOX_DRIVER_PATH, firefox_options=firefox_options)
            """全屏显示"""
            browser.maximize_window()
            time.sleep(3)
            browser.get('http://epub.sipo.gov.cn/')  # 进入中国专利公布公告首页
            browser.implicitly_wait(20)
            # TODO 默认选中第一个数据集，若有日期要求，需要自行确定数据集位置
            browser.find_element_by_xpath("/html/body/dl/dd/ol/li[" + str(data_type_patent[data_index]) + "]/a").click()  # 找到第一个数据集
        except:
            browser.quit()
            print('第{0}次尝试失败！'.format(item))
            continue
    time.sleep(2)
    browser.find_element_by_xpath('/html/body/div[3]/div[2]/dl/dt/select/option[2]').click()
    return browser, CNIPA_conn, CNIPA_cursor, insert_sql

def date_convert(value):
    try:
        try:
            try:
                create_date = datetime.datetime.strptime(value, "%Y.%m.%d").date()
            except:
                create_date = datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except:
            create_date = datetime.datetime.strptime(value, "%Y/%m/%d %H:%M:%S").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date

def seleniumSpider(browser, CNIPA_conn, CNIPA_cursor, insert_sql):
    global page

    flag = False
    current_page = start_page

    # 字段解析与插入数据库
    for page in range(start_page, end_page):

        browser.switch_to.window(browser.window_handles[-1])
        time.sleep(2)
        browser.implicitly_wait(20)
        browser.switch_to.window(browser.window_handles[-1])
        try:
            item_nodes = browser.find_elements_by_css_selector(".cp_linr")
            for item_node in item_nodes:
                browser.switch_to.window(browser.window_handles[-1])
                name = item_node.find_elements_by_css_selector(' h1')[0].text.split(' ')[1]
                info = item_node.find_elements_by_css_selector(' ul li')
                browser.implicitly_wait(20)
                if data_index == 1:
                    info_list = [item.text.replace('  全部', '').replace('\u2002', '').split('：')[1] for item in info if item.text != '' and '同一申请的已公布的文献号：' not in item.text and '申请公布日：' not in item.text]
                else:
                    info_list = [item.text.replace('  全部', '').replace('\u2002', '').split('：')[1] for item in info if item.text != '']
                info_list[1] = date_convert(info_list[1])
                info_list[3] = date_convert(info_list[3])
                CNIPA_cursor.execute(insert_sql, (name, info_list[0], info_list[1], info_list[2], info_list[3],
                                                  info_list[4], info_list[5], info_list[6], info_list[7]))
                CNIPA_conn.commit()
        except:
            time.sleep(5)
            browser.switch_to.window(browser.window_handles[-1])

            item_nodes = browser.find_elements_by_css_selector(".cp_linr")
            for item_node in item_nodes:
                browser.switch_to.window(browser.window_handles[-1])
                name = item_node.find_elements_by_css_selector(' h1')[0].text.split(' ')[1]
                info = item_node.find_elements_by_css_selector(' ul li')
                browser.implicitly_wait(20)
                if data_index == 1:
                    info_list = [item.text.replace('  全部', '').replace('\u2002', '').split('：')[1] for item in info if item.text != '' and '同一申请的已公布的文献号：' not in item.text and '申请公布日：' not in item.text]
                else:
                    info_list = [item.text.replace('  全部', '').replace('\u2002', '').split('：')[1] for item in info if item.text != '']
            info_list[1] = date_convert(info_list[1])
            info_list[3] = date_convert(info_list[3])
            CNIPA_cursor.execute(insert_sql, (name, info_list[0], info_list[1], info_list[2], info_list[3],
                                              info_list[4], info_list[5], info_list[6], info_list[7]))
            CNIPA_conn.commit()

        # 进入下一页
        browser.switch_to.window(browser.window_handles[-1])
        next = browser.find_elements_by_xpath("//div[@class='next']/a[last()]")[0].text
        if next == '>':
            try:
                browser.switch_to.window(browser.window_handles[-1])
                browser.find_elements_by_xpath("//div[@class='next']/a[last()]")[0].click()
                browser.implicitly_wait(20)
                logger.info('当前页数：{0}'.format(current_page))
                current_page += 1
            except:
                browser.switch_to.window(browser.window_handles[-1])
                time.sleep(10)
        else:
            logger.info('{0}：全部页面已遍历完成'.format(data_label_patent[data_index]))
            flag = True
            return flag
            break

def main():
    global page

    start_time = time.time()
    logger.info('开始爬取{0}的全部专利'.format(data_label_patent[data_index]))
    browser, CNIPA_conn, CNIPA_cursor, insert_sql = setup()
    try:
        flag = seleniumSpider(browser, CNIPA_conn, CNIPA_cursor, insert_sql)
        if flag == True:
            logger.info('{0}：全部页面已遍历完成'.format(data_label_patent[data_index]))
    except Exception as e:
        logger.error('程序报错：' + e)
        logger.warning('中途停止, 页面停止在：{0}页'.format(page))

    browser.quit()
    end_time = time.time()  # 结束时间
    cost_time = end_time - start_time  # 总运行时间，并按时分秒完成输出
    print('本次运行耗时：{0}时{1}分{2}秒 '.format(int(cost_time / 3600), int((cost_time / 60) % 60), int(cost_time % 60)))


if __name__ == '__main__':
    """
    基于selenium对CNIPA(中国专利公告网) http://epub.sipo.gov.cn/，7.9与7.12公告的发明专利、发明授权、实用新型和外观设计四类进行爬取
    """
    main()


