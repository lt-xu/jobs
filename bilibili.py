# encoding = 'utf-8
from selenium import webdriver
import time
from lxml import etree
import pymongo

def get_all_jobs():
    driver = webdriver.Firefox()
    url = 'https://campus.bilibili.com/activity-campus2019.html'
    driver.get(url)
    time.sleep(1)
    driver.find_element_by_xpath(
        u"(.//*[normalize-space(text()) and normalize-space(.)='前往官网'])[1]/following::button[1]").click()
    time.sleep(1)
    html = driver.page_source
    # print(html)
    root = etree.HTML(html)
    job_nodes = root.xpath('.//div[@class="job"]')
    for job_node in job_nodes:
        title = job_node[0].text              #第一个子节点
        location = '上海'
        responsibilities = job_node[2][0].tail.split('\n')    #职位描述整体为同一个str，split成list
        qualifications = job_node[3][0].tail.split('\n')
        if db.bilibili.find_one({'title':title}) is None:
            db.bilibili.insert_one({
                'title':title,
                'location':location,
                'responsibilities':responsibilities,
                'qualifications':qualifications
            })
    driver.close()

def add_time_info():   #笔试面试等信息
    if db.bilibli.find_one({'info':{'$exists':True}}) is None:
        db.bilibili.insert_one({'info':'内推：8.15-10.16 网申：8.24-10.16 笔试：第一批9.7 第二批9.21 第三批10.18 面试：内推8月下旬-9月 网申9月-10月 （可远程面试）2018年宣讲城市：成都 武汉 合肥 北京 上海 广州'})

if __name__ == '__main__':
    client = pymongo.MongoClient()
    db = client['jobs']
    # add_time_info()
    # get_all_jobs()
