#encoding = 'utf-8'
import requests
from selenium import webdriver
from lxml import etree
import re
import time
import pymongo

def job_urls(html):
    root = etree.HTML(html)
    reaults = []
    nodes = root.xpath('.//div[@class="results-3lLiS"]/a')
    for node in nodes:
        reaults.append(node.attrib['href'])
    return reaults

def get_jobs_details(url):
    while True:   #确保webdriver get到的网址正确
        driver.get(url)
        time.sleep(1)
        current_url = driver.current_url
        if current_url != 'https://app.mokahr.com/campus_apply/xiaomi/306': #经常出现weidriver get到此网址的bug
            break
    detail_html = driver.page_source
    root = etree.HTML(detail_html)
    location = root.xpath('.//div[@class="job-details-3a_UI"]//div[@class="job-info-sCGWE"]//span[@class="status-item-FsFJX"]')[2].text
    if location.find("等") != -1:  #有多处工作地点时更新为具体工作地点
        while True:       #click()偶尔会失灵 发现具体location未出现时，反复点击
            element = driver.find_element_by_xpath('.//div[@class="job-details-3a_UI"]//div[@class="job-info-sCGWE"]//span[@class="more-info-toggle-FMBPT"]')
            element.click()
            time.sleep(1)
            detail_html = driver.page_source
            root = etree.HTML(detail_html)
            length = len(root.xpath('.//div[@class="job-details-3a_UI"]//div[@class="job-info-sCGWE"]//div[@class="more-info-1mtyY"]/div'))
            if length == 2:                    #具体location在第二个div中
                break
        location = root.xpath('.//div[@class="more-info-1mtyY"]/div')[1].text
    title = str(root.xpath('.//div[@class="title-3rkKX"]/text()')[0])  # title前后有注释句包围，text()获得title
    list_node=root.xpath('.//div[@class="list-K5s74"]/div')[1]
    responsibilities = []               #岗位描述
    qualifications = []                 #岗位要求
    flag = 1   #岗位要求list_node的child中位置
    for child in list_node[1:]:                   #内容中有href等节点，用tostring保存这些节点信息
        content = str(etree.tostring(child,encoding='utf-8'),encoding='utf-8')[3:-4]  # encoding防止中文乱码，tostring()返回值为Bytes，str[3:-4]去掉<p></p> 截取中间部分
        if content == '<strong>任职要求：</strong>':
            break
        flag += 1
        if content != '<br/>' and content != '<br>':
            responsibilities.append(content)
    for child in list_node[flag+1:]:
        content = str(etree.tostring(child, encoding='utf-8'), encoding='utf-8')[3:-4]  # str[3:-4]去掉<p></p> 截取中间部分
        if content != '<br/>' and content != '<br>':
            qualifications.append(content)
    if db.xiaomi.find_one({'title':title}) is None:
        db.xiaomi.insert_one({
            'title':title,
            'location':location,
            'responsibilities':responsibilities,
            'qualifications':qualifications,
        })
    print(title,'',location,'')


def get_jobs_per_page(base_url):
    driver.get(base_url)
    time.sleep(1)
    html = driver.page_source
    append_urls = job_urls(html)
    for append_url in append_urls:
        # print(append_url)
        url = re.match(r'(.+)jobs', base_url).group(1) + append_url[2:]
        print(url)
        get_jobs_details(url)

def get_all_jobs():
    driver = webdriver.Firefox()
    base_url = 'https://app.mokahr.com/campus_apply/xiaomi/306#/jobs?department=[13839]&page=1&zhineng=5286&_k=7okexh'
    get_jobs_per_page(base_url)
    base_url = 'https://app.mokahr.com/campus_apply/xiaomi/306#/jobs?department=[13839]&page=2&zhineng=5286&_k=7okexh'
    get_jobs_per_page(base_url)
    base_url = 'https://app.mokahr.com/campus_apply/xiaomi/306#/jobs?department=[13839]&page=3&zhineng=5286&_k=7okexh'
    get_jobs_per_page(base_url)
    driver.close()


def add_time_info():   #笔试面试等信息
    if db.xiaomi.find_one({'info':{'$exists':True}}) is None:
        db.xiaomi.insert_one({'info':'消息：8.15 内推：8.15-9.15 网申：8.15-12月初 笔试：9.20和27号 面试：8月底-12月中 offer：10月-12月'})


def update_jobs_info():
    pass

if __name__ == '__main__':
    client = pymongo.MongoClient()
    db = client['jobs']
    # add_time_info()
    # get_all_jobs()

