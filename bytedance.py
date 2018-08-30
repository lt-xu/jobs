#encoding = 'utf-8
from selenium import webdriver
from lxml import etree
import time
import re
import pymongo
import json
import requests

def job_details(job_id):
    base_url = 'https://job.bytedance.com/api/recruitment/position/'
    job_json = base_url + job_id + '/'
    html = requests.get(job_json)
    content = html.content
    json_dict = json.loads(content)
    content_dict = json_dict['position']
    title = content_dict['name']
    id = content_dict['id']
    location = content_dict['city']
    category = content_dict['category']
    url = 'https://job.bytedance.com/job/detail/'+job_id
    responsibilities = content_dict['description'].split('\n')
    qualifications = content_dict['requirement'].split('\n')
    print(title+location)
    if db.bytedance.find_one({'id':id}) is None:
        db.bytedance.insert_one({
            'title': title,
            'location': location,
            'id':id,
            'category':category,
            'url':url,
            'responsibilities':responsibilities,
            'qualifications':qualifications
        })

def get_all_jobs(url,total_page):
    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(1)
    job_ids = []       #所有page的所有job_id
    for page in range(1,total_page+1):
        driver.find_element_by_xpath(u'.//button[@class="btn-prev"]/following::li[{}]'.format(page)).click()
        time.sleep(1)
        html = driver.page_source
        root = etree.HTML(html)
        job_nodes = root.xpath('.//td[@class = "el-table_1_column_1   content-cell"]')
        for job_node in job_nodes:
            url = job_node.xpath('.//a')[0].attrib['href']
            job_ids.append(re.search(r'^/job/detail/(\d{5})',url).group(1))
    # print(job_urls)
    for job_id in job_ids:
        job_details(job_id)
    driver.close()

def add_time_info():   #笔试面试等信息
    if db.bytedance.find_one({'info':{'$exists':True}}) is None:
        db.bytedance.insert_one({'info':'网申及内推：8.1-12.31 宣讲会：8月底-10月中旬 笔试：8月中旬-1月中旬 面试：8月中旬-1月中旬 offer：9月中旬开始'})

if __name__ == '__main__':
    client = pymongo.MongoClient()
    db = client['jobs']
    url = 'https://job.bytedance.com/campus/position?summary=873&city=&q1=&position_type='
    total_page = 5
    # add_time_info()
    # get_all_jobs(url,total_page)
