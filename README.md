# weibo_hot_search_and_comment_crawler
微博热搜爬虫，并且采集热搜新闻下评论的数据，可以弹出弹窗自动输入热搜链接进行评论采集，现在设置是一个热搜下10条新闻，每条新闻20条评论，总共采集10*20=200条评论

# 1、运行步骤

## 1.1 数据库建表

```mysql
## 建库、建表语句
# 新建数据库
CREATE DATABASE weibo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 选择数据库
USE weibo;

# 新建热搜表
CREATE TABLE hot_search (
    date DATE NOT NULL,
    time TIME NOT NULL,
    hot_index INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    raw_hot INT NOT NULL,
    label_name VARCHAR(255) NOT NULL,
    url VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

# 新建评论表
CREATE TABLE comment (
    new_id VARCHAR(20) NOT NULL,
    author_name VARCHAR(50) NOT NULL,
    fans VARCHAR(20) NOT NULL,
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
```

## 1.2 更改数据库配置

hot_search.py第9行

![image-1](/img/1.png)

mian.py第37行

![image-1](/img/2.png)

## 1.3 运行hot_search.py

该文件用来采集所有热搜

![image-1](/img/3.png)

## 1.4 运行main.py文件

在输入框输入刚才采集的某个热搜的链接，即可启动爬虫采集该热搜下的10条新闻，及每条新闻下的20条评论

![image-1](/img/4.png)

采集结果：

![image-1](/img/5.png)

# 2、后续

后面想采集更多新闻可以修改代码，已写好注释。
