#encoding = 'utf-8
from selenium import webdriver
from lxml import etree
import time
import re
import pymongo
def job_detail(url):
    while True:   #确保webdriver get到的网址正确 和 内容加载完毕，否则重新载入   运行时网络及其不通畅
        driver.get(url)
        driver.implicitly_wait(10)
        driver.find_elements_by_class_name('slds-p-vertical--medium')
        current_url = driver.current_url
        html = driver.page_source
        root = etree.HTML(html)
        if current_url == url and len(root.xpath('.//h1')) != 0:  #测试是否抓取到<h1>
            break
    title = root.xpath('.//h1')[0].text.strip()
    text = root.xpath('.//div[@class="slds-size--1-of-3"]')[0].text
    location = re.search(r'(成都|北京)',text).group(1) #北京or成都
    postDate = re.search(r'(\d{4}-\d{1,2}-\d{1,2})',root.xpath('.//div[@class="slds-size--1-of-3"]')[1].text).group(1) #匹配日期
    list_node = root.xpath('.//div[@class="slds-p-vertical--medium"]')[0]
    responsibilities = []               # 岗位描述
    qualifications = []                 # 岗位要求
    pluses = []                         # 加分项
    flag = 0
    for detail_node in list_node:
        detail = detail_node.tail   #detail_node is <br>
        if detail == '任职资格' or detail == '任职要求：' or detail == '任职资格：':      #每一项的区别在空格和：
            break
        flag += 1
        if detail != '<br/>' and detail != '<br>' and detail:
            responsibilities.append(detail)
    for detail_node in list_node[flag+1:]:
        detail = detail_node.tail   #detail_node is <br>
        if detail == '具有以下条件者优先考虑：' or detail == '具有以下条件者优先考虑： ' or detail == '加分项：':
            break
        flag += 1
        if detail != '<br/>' and detail != '<br>' and detail != '任职资格' and detail:
            qualifications.append(detail)
    for detail_node in list_node[flag+2:]:  #测试表明需要+2
        detail = detail_node.tail   #detail_node is <br>
        if detail != '<br/>' and detail != '<br>' and detail:
            pluses.append(detail)
    if db.sina.find_one({'title':title}) is None:
        db.sina.insert_one({
            'title':title,
            'location':location,
            'url':url,
            'postDate':postDate,
            'responsibilities':responsibilities,
            'qualifications':qualifications,
            'pluses':pluses,
        })


def get_jobs_per_page():
    html = driver.page_source
    root = etree.HTML(html)
    job_list = root.xpath('.//tbody/tr')
    for job in job_list:
        job_url = job[0][0].attrib['href']
        job_detail(job_url)

def get_all_jobs():
    driver.get('http://sina.gllue.me/portal/campusposition/list')
    time.sleep(5)      #运行时网络及其不通畅
    #研发类 第一页
    driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='全部'])[2]/following::span[1]").click()
    time.sleep(1)
    driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='上一页'])[1]/following::button[1]").click()
    time.sleep(1)
    get_jobs_per_page()
    #重新载入职位列表
    driver.get('http://sina.gllue.me/portal/campusposition/list')
    time.sleep(5)
    #研发类 第二页
    driver.find_element_by_xpath(
        u"(.//*[normalize-space(text()) and normalize-space(.)='全部'])[2]/following::span[1]").click()
    time.sleep(1)
    driver.find_element_by_xpath(
        u"(.//*[normalize-space(text()) and normalize-space(.)='上一页'])[1]/following::button[2]").click()
    time.sleep(1)
    get_jobs_per_page()

def add_time_info():   #笔试面试等信息
    flag = False      #info是否写入的标志
    for doc in db.sina.find():
        if 'info' in doc:   #判断doc（dict）中是否有info（key）
            flag = True
    if not flag:      #不存在info 则写入
        db.sina.insert_one({'info':'消息：8.6 网申&内推：8.6-9.14 宣讲：9月除 笔试：9.15和16 面试：9月底（地点：哈尔滨 沈阳 成都 西安 武汉 北京） offer 10月中下旬'})

if __name__ == '__main__':
    client = pymongo.MongoClient()
    db = client['jobs']
    # driver = webdriver.Firefox()
    # add_time_info()
    # get_all_jobs()
    # driver.close()




