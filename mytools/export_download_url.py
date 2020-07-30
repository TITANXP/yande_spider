from pymongo import MongoClient
import glob
import datetime
import shutil

if __name__ == '__main__':
    # like_files_path =
    files = glob.glob('.\download-URLs\like\*.txt')
    like_file_path = files[-1]
    print(like_file_path)
    dates = list(map(int, like_file_path.split('\\')[-1].replace('like.txt', '').split('-')))

    client = MongoClient('localhost', 27017)
    db = client['yande']
    table = db['pic_master']
    ql = {
        # "date": {"$gte": datetime.datetime.now() - datetime.timedelta(hours=1)}
        "date": {"$gte": datetime.datetime(*dates)}
    }
    data = table.find(ql)
    count = data.count()

    for i in data:
        print(i)

    print(count)
    with open(like_file_path, 'r') as f:
        count = 0
        for l in f.readlines():
            count+=1
        print("文件中有", count, "行")

    shutil.copy(like_file_path, r"C:\Users\LiQi\OneDrive\文档\yande")