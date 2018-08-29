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
        if current_url != 'https://app.mokahr.com/campus_apply/zhihu': #经常出现weidriver get到此网址的bug
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
    responsibilities = []               #岗位描述
    qualifications = []                 #岗位要求
    pluses = []                         #加分项
    list_node = root.xpath('.//div[@class="list-K5s74"]/div')[1]
    content_nodes = list_node.xpath('./ul')
    length = len(content_nodes)
    if length > 0:               #用<ul><li>节点组成内容，条理清楚
        li_nodes = content_nodes[0]  # 岗位描述内容
        for li_node in li_nodesdo
            responsibilities.append(li_node.text)
        li_nodes = content_nodes[1]  # 岗位要求内容
        for li_node in li_nodes:
            qualifications.append(li_node.text)
        if len(content_nodes) == 3:
            li_nodes = content_nodes[2]  # 加分项内容
            for li_node in li_nodes:
                pluses.append(li_node.text)
        # print('3 ',title, '', location, '',str(len(responsibilities)),str(len(qualifications)),str(len(pluses)))
    else:                               #完全由<p>节点组成内容，不调理清楚，两套规则，真辣鸡
        # print("例外：", url, ' ', title)
        flag = 0  # 岗位要求以及加分项在list_node的child中位置
        for child in list_node[0:]:  # 若内容中有href等节点，用tostring保存这些节点信息
            content = str(etree.tostring(child, encoding='utf-8'), encoding='utf-8')[
                      3:-4]  # encoding防止中文乱码，tostring()返回值为Bytes，str[3:-4]去掉<p></p> 截取中间部分
            if content == '<strong>任职资格</strong>' or content == '<strong>职位要求</strong>':
                break
            flag += 1
            if content != '<br/>' and content != '<br>':
                responsibilities.append(content)
        for child in list_node[flag + 1:]:
            content = str(etree.tostring(child, encoding='utf-8'), encoding='utf-8')[3:-4]  # str[3:-4]去掉<p></p> 截取中间部分
            if content == '<strong>加分项</strong>':
                break
            flag += 1
            if content != '<br/>' and content != '<br>' and content != '<strong>\ufeff</strong>':
                qualifications.append(content)
        for child in list_node[flag+1:]:
            content = str(etree.tostring(child, encoding='utf-8'), encoding='utf-8')[3:-4]  # str[3:-4]去掉<p></p> 截取中间部分
            if content != '<br/>' and content != '<br>' and content != '<strong>加分项</strong>':
                pluses.append(content)
        # print('0 ',title, '', url, '',str(len(responsibilities)),str(len(qualifications)),str(len(pluses)))
        # print('responsibilities:',responsibilities)
        # print('qualifications:',qualifications)
        # print('plusers:',pluses)

    if db.zhihu.find_one({'title':title}) is None:
        db.zhihu.insert_one({
            'title':title,
            'location':location,
            'url':url,
            'responsibilities':responsibilities,
            'qualifications':qualifications,
            'pluses':pluses,
        })



def get_jobs_per_page(base_url):
    driver.get(base_url)
    time.sleep(1)
    html = driver.page_source
    # driver.close()
    append_urls = job_urls(html)
    for append_url in append_urls:
        # print(append_url)
        url = re.match(r'(.+)jobs', base_url).group(1) + append_url[2:]
        # print(url)
        get_jobs_details(url)

def get_all_jobs():
    #岗位名相同，但所属事业部不同，归为一document，不做区分
    driver = webdriver.Firefox()
    base_url = 'https://app.mokahr.com/campus_apply/zhihu#/jobs?zhineng=6499&page=1&_k=m4efkx'
    get_jobs_per_page(base_url)
    base_url = 'https://app.mokahr.com/campus_apply/zhihu#/jobs?zhineng=6499&page=2&_k=m4efkx'
    get_jobs_per_page(base_url)
    base_url = 'https://app.mokahr.com/campus_apply/zhihu#/jobs?zhineng=6499&page=3&_k=m4efkx'
    get_jobs_per_page(base_url)
    driver.close()

def add_time_info():   #笔试面试等信息
    flag = False      #info是否写入的标志
    for doc in db.zhihu.find():
        if 'info' in doc:   #判断doc（dict）中是否有info（key）
            flag = True
    if not flag:      #不存在info 则写入
        db.zhihu.insert_one({'info':'消息：8.1 网申/内推：8.1-9.30 openDay:9月除 在线笔试:8月底-10月出 宣讲+面试9月初-10月中 offer：9月中-10月底'})


def update_jobs_info():
    #原页面写的太混乱，‘前端开发工程师（校招成都）’此岗位的编写独树一帜，前文所写的爬取程序不再适应，特此更改
    doc = db.zhihu.find_one({'title':'前端开发工程师（校招成都）'})
    responsibilities = ['与产品设计师、后端工程师协作，参与设计和开发知乎产品；','包括但不限于知乎主站、APP 、小程序等方向。']
    qualifications=['有扎实的前端技术基础，包括但不限于 HTML、CSS、JavaScript、DOM；','对计算机相关基础知识有较好的理解，熟悉服务端开发技术；','熟悉常见的前端框架、库、工具，例如：jQuery、AngularJS、Backbone.js、React、Grunt、Gulp 等；','有复杂用户界面与交互应用开发经验，在乎设计细节，能够发现并反馈设计稿中的缺陷。']
    pluses = ['有复杂项目的架构设计经验或规范制定经验；','有过深入研究某一方面的前端技术的经验，能够有自己的理解和看法；']
    item = {
            'title':doc['title'],
            'location':doc['location'],
            'url':doc['url'],
            'responsibilities':responsibilities,
            'qualifications':qualifications,
            'pluses':pluses,
        }
    db.zhihu.update({"_id": doc["_id"]},{'$set':item})

if __name__ == '__main__':
    client = pymongo.MongoClient()
    db = client['jobs']
    # add_time_info()
    # get_all_jobs()
    # update_jobs_info()


