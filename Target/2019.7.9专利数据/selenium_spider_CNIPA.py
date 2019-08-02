# -*- coding: utf-8 -*-
# 开发团队   ：CSSC_linyuanlab
# 开发人员   ：yyc
# 开发时间   ：2019/7/11  17:27
# 文件名称   ：selenium_spider_CNIPA.py
# 开发工具   ：PyCharm

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
import os
import sys
import pandas as pd
# from urllib import request
# px = request.ProxyHandler({'https':'114.225.168.213:53128'})
# opener = request.build_opener(px)
# req = request.Request("http://epub.sipo.gov.cn/")
# res = opener.open(req)
# request.install_opener(opener)



"""爬虫控制"""
data_index = 0

project_path = os.path.abspath(os.path.dirname(sys.argv[0]))
long_long_sleep = 20
long_sleep = 10
middle_sleep = 5
quick_sleep = 2
page_sleep = 20
items_per_page = 10
data_type_patent = [5,6,7,8]
# data_type_patent = [1,2,3,4]
data_name_patent = ['CN_patent_invention_published_709','CN_patent_invention_authorized_709',
                    'CN_patent_utility_new_709','CN_patent_appearance_designed_709']
attr_locate_list = [[1,2,3,4,5,6,8,9], [1,2,3,4,7,8,10,11],[1,2,3,4,5,6,8,9], [1,2,3,4,5,6,8,9]]

attr_name_list = ['item', 'name', 'authorization_notice_id', 'authorized_announcement_date',
                  'filing_id', 'filing_date', 'patentee', 'designer','address', 'Int.Cl.']
start_page = 1000
end_page = 2000

# browser = webdriver.Firefox(executable_path=r'C:\Users\Administrator\Desktop\YEGEGE\GitHub_C2C\PatentCountryInnovation\C2C\enforcement\geckodriver.exe')
# browser = webdriver.Firefox(executable_path=r'C:\Users\yeyuc\Desktop\GitHub_C2C\patent_country_innovation\C2C\enforcement\geckodriver.exe')


def setup():
    browser = webdriver.Firefox(executable_path=project_path + '\\enforcement\\geckodriver.exe')  # 驱动路径（相对）
    time.sleep(middle_sleep)
    browser.get('http://epub.sipo.gov.cn/')  # 进入中国专利公布公告首页
    time.sleep(quick_sleep)
    browser.find_element_by_xpath(
        "/html/body/dl/dd/ol/li[" + str(data_type_patent[data_index]) + "]/a").click()  # 找到第一个数据集
    time.sleep(long_sleep)
    browser.find_element_by_xpath('/html/body/div[3]/div[2]/dl/dt/select/option[2]').click()
    return browser


def locateAndRest(browser):
    time.sleep(middle_sleep)
    browser.switch_to.window(browser.window_handles[-1])
    time.sleep(middle_sleep)

def seleniumSpider(browser, data=''):
    item_count = (start_page-1)*10
    CN_patent = data
    # 从列表展示开始爬取
    for page in range(start_page, end_page):
        time.sleep(page_sleep)
        # if page == start_page:
        if  page <= 10 or page == start_page:
            browser.switch_to.window(browser.window_handles[-1])
            browser.find_element_by_xpath("//*[@id='pn']").send_keys(str(page))
            browser.implicitly_wait(30)
            browser.find_element_by_xpath("//*[@id='pn']").send_keys(Keys.ENTER)
            browser.implicitly_wait(30)

        locateAndRest(browser)
        for item1 in range(1, items_per_page+1):
            spider_list = []
            spider_list.append(item_count+1)
            browser.switch_to.window(browser.window_handles[-1])
            try:
                name = browser.find_element_by_xpath("/html/body/div[3]/div[2]/div["+str(item1)+"]/div[2]/h1").text
            except:
                locateAndRest(browser)
                try:
                    name = browser.find_element_by_xpath("/html/body/div[3]/div[2]/div[" + str(item1) + "]/div[2]/h1").text
                except:
                    CN_patent.to_csv(data_name_patent[data_index] + '.csv', encoding=('GB18030'), index=False)
                    # break

            regex_str = '.*? (.*$)'
            try:
                name = re.match(regex_str, name).group(1)
            except:
                name = name
            spider_list.append(name)

            for item2 in attr_locate_list[data_index]:
                browser.switch_to.window(browser.window_handles[-1])
                try:
                    attr = browser.find_element_by_xpath("/html/body/div[3]/div[2]/div["+str(item1)+"]/div[2]/ul/li["+str(item2)+"]").text
                except:
                    locateAndRest(browser)
                    attr = browser.find_element_by_xpath(
                        "/html/body/div[3]/div[2]/div[" + str(item1) + "]/div[2]/ul/li[" + str(item2) + "]").text
                regex_str = '.*?：(.*$)'
                try:
                    attr = re.match(regex_str, attr).group(1)
                except:
                    attr = attr
                if '全部' in attr:
                    attr=attr.replace('全部', '').strip(' ')
                spider_list.append(attr)
            if item_count == 0:
                CN_patent = pd.DataFrame([1])
                CN_patent = CN_patent.rename(columns={0: 'item'})  # 更改第一列列名为'ctry'
                for i in range(1, 10):
                    CN_patent.insert(i, attr_name_list[i], spider_list[i])
            else:
                insertRow = pd.DataFrame([spider_list], columns=attr_name_list)
                above = CN_patent.loc[:item_count]
                below = CN_patent.loc[item_count + 1:]
                CN_patent = above.append(insertRow, ignore_index=True).append(below, ignore_index=True)
            item_count += 1
            if item_count % 10 == 0:
                CN_patent.to_csv(data_name_patent[data_index] + '.csv', encoding=('GB18030'), index=False)
        # browser.implicitly_wait(20)
        browser.switch_to.window(browser.window_handles[-1])
        next = browser.find_element_by_xpath("/html/body/div[3]/div[2]/div[11]").text
        if page >= 10:
            if '<' in next:
                next = next.replace('<', '< ')
            if '>' not in next:
                break
            else:
                next = next.replace('>', '> ')
            next = next.replace('...', '... ')
            next = next.split().index('>')
            browser.switch_to.window(browser.window_handles[-1])
            if page == 1:
                browser.find_element_by_xpath("/html/body/div[3]/div[2]/div[11]/a[" + str(next) + "]").click()
            else:
                browser.find_element_by_xpath("/html/body/div[3]/div[2]/div[11]/a[" + str(next + 1) + "]").click()
            browser.implicitly_wait(30)
            time.sleep(page_sleep)



    CN_patent.to_csv(data_name_patent[data_index]+'.csv', encoding=('GB18030'), index=False)



def main():
    start_time = time.time()

    flag = 1
    if start_page != 1:
        try:
            CN_patent = pd.read_csv(data_name_patent[data_index] + '.csv', encoding=('GB18030'))
        except Exception as e:
            print(data_name_patent[data_index] + '.csv' + '不存在')
            flag= 0
        if flag == 1:
            browser = setup()
            try:
                seleniumSpider(browser, data=CN_patent)
            except Exception as e:
                print('中途停止')
    else:
        browser = setup()
        try:
            seleniumSpider(browser)
        except Exception as e:
            print(e)
            print('中途停止')

    end_time = time.time()  # 结束时间
    cost_time = end_time - start_time  # 总运行时间，并按时分秒完成输出
    print('本次运行耗时：{0}时{1}分{2}秒 '.format(int(cost_time / 3600), int((cost_time / 60) % 60), int(cost_time % 60)))


if __name__ == '__main__':
    main()


