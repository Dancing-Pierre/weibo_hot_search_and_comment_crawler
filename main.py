import tkinter as tk
from tkinter import messagebox
import threading
import datetime
import json
import re
import time

import pymysql
import requests
from lxml import etree

# 创建主窗口
root = tk.Tk()
root.title("爬虫程序")
# 设置窗口大小
root.geometry("400x150")
# 创建标签和输入框
label_url = tk.Label(root, text="请输入链接：")
entry_url = tk.Entry(root, width=50)

# 请求头携带登录凭证，要经常换
header = {
    "cookie": "_s_tentry=weibo.com; Apache=3001527063820.9146.1681480670367; SINAGLOBAL=3001527063820.9146.1681480670367; ULV=1681480670407:1:1:1:3001527063820.9146.1681480670367:; WBtopGlobal_register_version=2023041500; SSOLoginState=1681490965; SUB=_2A25JPfRFDeRhGeFK7VEU-SrMzzyIHXVqwZwNrDV8PUJbkNANLRWgkW1NQxvJYnWWvwLQjhxOKRMLkviKLNfvlzP0; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Whz9fyXo67C4.SSZXSDEglz5NHD95QNShq0SK.XehB7Ws4Dqcjci--fi-82i-2Xi--ciKL8iK.fi--Xi-zRiKn7i--NiKnpi-8si--ci-zRiKnfi--Ni-2NiKyF; PC_TOKEN=6df7f7af5a; WBStorage=4d96c54e|undefined",
    "referer": "https://weibo.com/",
    "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}
# 建立数据库连接
cnx = pymysql.connect(host='localhost', port=3306, user='root', password='123456',
                      db='weibo', charset='utf8mb4')
# 创建游标
cursor = cnx.cursor()

# 创建一个名为comment的表
create_table_sql = '''
    CREATE TABLE comment (
    new_id VARCHAR(20) NOT NULL,
    author_name VARCHAR(50) NOT NULL,
    fans VARCHAR(20) NOT NULL,
    forward VARCHAR(20) NOT NULL,
    news_follow VARCHAR(20) NOT NULL,
    comment_id VARCHAR(20) NOT NULL,
    comment_text TEXT NOT NULL,
    comment_date DATE NOT NULL,
    comment_time TIME NOT NULL,
    floor_number INT NOT NULL,
    source VARCHAR(20) NOT NULL,
    user_name VARCHAR(50) NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    user_follow_count VARCHAR(20) NOT NULL,
    user_followers_count VARCHAR(20) NOT NULL,
    user_gender VARCHAR(5) NOT NULL,
    PRIMARY KEY (comment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
'''
cursor.execute(create_table_sql)


# 创建“开始爬取”按钮的回调函数
def start_spider():
    url = entry_url.get()
    root.quit()
    sa = run_spider(url)
    if sa == 2:
        messagebox.showinfo(title="提示", message="采集完毕！")


def tran_gender(gender_tag):
    """转换性别"""
    if gender_tag == 'm':
        return '男'
    elif gender_tag == 'f':
        return '女'
    else:  # -1
        return '未知'


def run_spider(url):
    close = 2
    a = requests.get(url=url, headers=header)
    response = etree.HTML(a.text)
    data = response.xpath('//div[@id="pl_feedlist_index"]//div[@action-type="feed_list_item"]')
    sum = 0
    for i in data:
        data_dict = {}
        sum = sum + 1
        # 新闻id
        news_id = ''.join(i.xpath('./@mid'))
        data_dict['news_id'] = news_id
        # 发布新闻的作者名字
        author_name = ''.join(i.xpath('.//div[@class="info"]/div[2]//text()')).replace('\n', '').replace('\r',
                                                                                                         '').replace(
            ' ', '')
        data_dict['author_name'] = author_name
        # 转发
        forward = ''.join(i.xpath('.//div[@class="card-act"]//li[2]//text()')).replace('转发', '').replace(' ', '')
        data_dict['forward'] = forward
        # 新闻点赞数
        news_follow = ''.join(i.xpath('.//div[@class="card-act"]//li[4]//text()'))
        data_dict['news_follow'] = news_follow
        # 带有作者id的链接
        author_url = ''.join(i.xpath('.//div[@class="info"]/div[2]/a[1]/@href'))
        # 正则取出作者id
        author_id = re.search(r'\/(\d+)\?', author_url)
        author_id = author_id.group()[1:-1]
        # 拼接作者详情页链接
        author_detail_url = f'https://weibo.com/ajax/profile/info?custom={author_id}'
        # 请求作者详情页拿粉丝之类的数据
        b = requests.get(url=author_detail_url, headers=header)
        response = json.loads(b.text)
        # 作者粉丝
        fans = response['data']['user']['followers_count']
        fans = f'{int(fans) / 10000}万'
        data_dict['fans'] = fans
        # 采集评论
        url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0&sudaref=weibo.com&display=0&retcode=6102'.format(
            news_id, news_id)
        c = requests.get(url=url, headers=header)
        print(c.text)
        try:
            data = json.loads(c.text)['data']['data']
            for i in data:
                # 评论id
                comment_id = i['id']
                # 评论详情
                comment_text = i['text']
                # 评论时间
                input_string = i['created_at']
                # 定义输入字符串和格式
                input_format = '%a %b %d %H:%M:%S %z %Y'
                # 将字符串转换为日期时间对象
                dt = datetime.datetime.strptime(input_string, input_format)
                # 将日期时间对象格式化为指定格式的字符串
                # 年月日
                output_format_1 = '%Y-%m-%d'
                comment_date = dt.strftime(output_format_1)
                # 时分秒
                output_format_2 = '%H:%M:%S'
                comment_time = dt.strftime(output_format_2)
                # 评论点赞数
                floor_number = i['floor_number']
                source = i['source'][2:]
                # 评论用户名称
                user_name = i['user']['screen_name']
                # 评论用户id
                user_id = i['user']['id']
                # 关注
                user_follow_count = i['user']['follow_count']
                # 粉丝
                user_followers_count = i['user']['followers_count']
                # 性别
                user_gender = tran_gender(i['user']['gender'])
                data = {'news_id': news_id, 'author_name': author_name, 'fans': fans, 'forward': forward,
                        'news_follow': news_follow, 'comment_id': comment_id,
                        'comment_text': comment_text, 'comment_date': comment_date, 'comment_time': comment_time,
                        'floor_number': floor_number, 'source': source, 'user_name': user_name, 'user_id': user_id,
                        'user_follow_count': user_follow_count, 'user_followers_count': user_followers_count,
                        'user_gender': user_gender}
                print(data)
                data_tuple = tuple(data.values())
                add_data = "INSERT INTO comment (new_id,author_name,fans,forward,news_follow,comment_id,comment_text,comment_date,comment_time,floor_number,source,user_name,user_id,user_follow_count,user_followers_count,user_gender) VALUES (%s, %s,%s,%s,%s, %s, %s,%s, %s,%s, %s,%s, %s, %s,%s, %s)"
                cursor.execute(add_data, data_tuple)
                cnx.commit()
        except:
            pass
        # 想爬几条新闻，限制两条
        if sum == 10:
            break
    return close


# 创建“开始爬取”按钮
button_start = tk.Button(root, text="开始爬取", command=start_spider)

# 将标签、输入框和按钮添加到主窗口
label_url.pack()
entry_url.pack()
button_start.pack()

# 进入事件循环
root.mainloop()
