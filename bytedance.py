#encoding = 'utf-8
from selenium import webdriver
from lxml import etree
import time
import re
import pymongo
import json
import requests
import jieba
import jieba.analyse
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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

def analyse():
    # 分析任职要求
    jobs = db.bytedance.aggregate([
        {"$group": {"_id": "$title", "qualifications": {"$first": "$qualifications"}}},
    ])      #去重，在字节跳动职位信息中，同一title，不同地点，视为不同岗位，所以岗位要求会重复

    qual_tests = ""    #任职要求总文本
    for job in jobs:
        if job['qualifications']:
            qual_test = ''.join(job['qualifications'])
            qual_tests += qual_test
    cut_text = " ".join(jieba.cut(qual_tests))
    keywords = jieba.analyse.extract_tags(cut_text,topK=500, withWeight=True,allowPOS=('a','e','n','nr','ns'))

    text_cloud = dict(keywords)
    # print(text_cloud)
    cloud = WordCloud(
        # 设置字体，不指定就会出现乱码
        font_path="/usr/share/fonts/winFonts/msyhbd.ttc",
        # 设置背景色
        background_color='white',
        # 词云形状
        # mask=color_mask,
        # 允许最大词汇
        max_words=2000,
        # 最大号字体
        max_font_size=40,
        height=500,
        width= 1000
    )
    wordcloud = cloud.generate_from_frequencies(text_cloud)
    wordcloud.to_file("1.jpg")  # 保存图片


    # Display the generated image:
    # the matplotlib way:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    return

if __name__ == '__main__':
    client = pymongo.MongoClient()
    db = client['jobs']
    url = 'https://job.bytedance.com/campus/position?summary=873&city=&q1=&position_type='
    total_page = 5
    analyse()
    # add_time_info()
    # get_all_jobs(url,total_page)
