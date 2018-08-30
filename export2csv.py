import csv
import pymongo

def export2csv(collection,file,access_mode='w'):
    doc = collection.find_one({'info': {'$exists': False}})
    fieldnames = ['_id', 'title','location','responsibilities','qualifications','pluses'] #固定这几项位置，优先显示
    keys = list(doc.keys())
    for key in keys:
        if key not in fieldnames:
            fieldnames.append(key)
    with open(file,access_mode,newline="") as csvfile:
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        for doc in collection.find({'info': {'$exists': False}}):
            writer.writerow(doc)





if __name__ == '__main__':
    client = pymongo.MongoClient()
    db = client['jobs']
    collection = db['bilibili']
    file = "jobs.csv"
    export2csv(collection,file,'w')
    collection = db['sina']
    export2csv(collection,file,'a')
    collection = db['xiaomi']
    export2csv(collection,file,'a')
    collection = db['zhihu']
    export2csv(collection,file,'a')
    collection = db['bytedance']
    export2csv(collection,file,'a')
    # with open(file,'r') as f:
    #     reader = csv.DictReader(f)
    #     for i in reader:
    #         print(i)