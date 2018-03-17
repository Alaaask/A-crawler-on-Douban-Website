# -*- coding: utf-8 -*-
import re
import requests
#import codecs
import time
import random
import queue
from bs4 import BeautifulSoup

# ------------------------------------------------ 参数设置 ------------------------------------------------
header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0','Connection':'keep-alive'}

# 暂定爬30部电影
count = 30

# cookie文件地址
cookie_addr = "E:\python project\cookie.txt"
# 写出文件地址 注意结尾多一个\
comment_addr0  = "E:\python project\douban\comment\\"
rating_addr0 = "E:\python project\douban\\rating\\"

# 从Coco这部电影开始20495023
# 从不离不弃开始26828548，这个评论很少，用作test
starturl = 'https://movie.douban.com/subject/20495023/?from=showing'
startid = 20495023

# urls用来存储待爬电影的id
urls = queue.Queue()
urls.put(startid)

# 爬过的电影的id的列表
# 维护它有序
crawledurls = []

# ---------------------------------------------------------------------------------------------------------

# 写循环实现遍历
# 选择广度优先
# 从‘喜欢这部电影的人也喜欢’里进行遍历
def get_next_urls():
        
    # 查找是否爬过
    # i == -1:爬过
    def search_urls(url):
        # 这一句是为了防止报错
        # 且当len(crawledurls) == 0时，不进入for循环，后面也不会跳不出while循环
        idx = -2
        for idx in range(len(crawledurls)):
            if crawledurls[idx] > url:
                break
            if crawledurls[idx] == url:
                idx = -1
                break
        
        # 如果是比列表中的id都大，上面没有考虑到
        if len(crawledurls) != 0 and crawledurls[-1] < url:
            idx = len(crawledurls)
            
        return idx
        
    next_id = urls.get()
    i = search_urls(next_id)
    while i == -1:
        next_id = urls.get()
        i = search_urls(next_id)
    
    # 维护crawledurls有序
    crawledurls.insert(i, next_id)
    
    next_url1 = 'https://movie.douban.com/subject/' + str(next_id) + '/comments'
    next_url2 = 'https://movie.douban.com/subject/' + str(next_id) + '/comments?start={}&limit=20&sort=new_score&status=P'
    next_url3 = 'https://movie.douban.com/subject/' + str(next_id) + '/?from=showing'

    return next_url1, next_url2, next_url3
        

def get_comment(html): 
    
    soup = BeautifulSoup(html,'lxml')
    
    # 类名(类名加点)comment 标签p
    comment_list = soup.select('.comment > p')
    
    # 翻后页
    # 首页的翻页链接只有一个，下一页就变成了第一个链接
    # 这里不能加 > 号
    if soup.select('#paginator a[class="next"]') != []:
        next_page = soup.select('#paginator a[class="next"]')[0].get('href')
    else:
        next_page = None
    
    # 获得评论时间
    date_nodes = soup.select('..comment-time')
    
    return comment_list,next_page,date_nodes
    
def write_comment(f, comment_list, date_nodes):
    
    for i in range(max(len(comment_list),len(date_nodes))):

        if i < len(comment_list):
            comment = comment_list[i].get_text().strip().replace("\n", "")
        else:
            comment = "No comment."
        
        if i < len(date_nodes):
            date = date_nodes[i].get_text().strip()
        else:
            date = "No date."
        
        f.writelines(comment +'\t'+ date + u'\n') # u表示unicode 会对\n进行处理
    

def get_href(html):
    
    soup = BeautifulSoup(html,'lxml')
    
    # 正则表达式匹配id
    pattern = re.compile('[0-9]+')
    
    # 将id加入待爬队列
    for j in range(len(soup.select('dt > a'))):
        href = soup.select('dt > a')[j].get('href')
        match = pattern.search(href).group()
        urls.put(int(match))
 
# 这里get了也写进文件了       
def get_write_rating(html,n):
    
    soup = BeautifulSoup(html,'lxml')
    
    title = soup.select('span[property="v:itemreviewed"]') # 这是个list
    
    # 文件路径
    # rating_addr = rating_addr0 + str(n) +"-" + title[0].get_text() + ".txt"
    # 纯数字文件名方便后续分词处理
    rating_addr = rating_addr0 + str(n) + ".txt"
    
    # 写入
    # 电影名 年份 得分 打分人数
    # 都先判断是否存在，因为有的电影真的不存在某些属性
    with open(rating_addr, 'a', encoding='utf-8') as f:
        
        f.writelines(title[0].get_text() + '\t' + u'\n')
        
        if len(soup.select('.year')) > 0:
            year = soup.select('.year')
            f.writelines(year[0].get_text() + '\t' + u'\n')
            
        if len(soup.select('strong[property="v:average"]')) > 0:
            rating = soup.select('strong[property="v:average"]') # = 旁边不能打空格
            f.writelines(rating[0].get_text() + '\t' + u'\n')
            
        if len(soup.select('a[class="rating_people"]')) > 0:
             rating_people = soup.select('a[class="rating_people"]')[0].get_text()
             f.writelines(rating_people + '\t' + u'\n')
        
        # 得分优于
        if  len(soup.select('.rating_betterthan')) > 0:
            rating_betterthan = soup.select('.rating_betterthan')
            rating_betterthan = rating_betterthan[0].get_text().strip().replace("\n", "")
            f.writelines(rating_betterthan + '\t' + u'\n')
        
        # 具体打分情况
        if len(soup.select('div[class="ratings-on-weight"] > div[class="item"]')) > 0:
            ratings_on_weight = soup.select('div[class="ratings-on-weight"] > div[class="item"]')
            for row in ratings_on_weight:
                row = row.get_text().strip().replace("\n", "")
                f.writelines(row + '\t' + u'\n')
        
    f.close()
    
    return title[0].get_text()


if __name__ == '__main__':
    
    # 设置cookie
    f_cookies = open(cookie_addr, 'r')
    cookies = {}
    
    for line in f_cookies.read().split(';'):
        name, value = line.strip().split('=', 1)
        cookies[name] = value
    
    # 爬count部电影就停止
    for n in range(count):
        
        # 获得url
        next_url1, next_url2, next_url3 = get_next_urls()
        
        # 爬href和评分
        html = requests.get(next_url3, cookies=cookies, headers=header).content
        get_href(html)
        movie_title = get_write_rating(html,n)
        
        # 爬短评
        html = requests.get(next_url2, cookies=cookies, headers=header).content
        
        # 文件路径
        # comment_addr = comment_addr0 + str(n) +"-" + movie_title + ".txt"
        # 纯数字文件名方便后续分词处理
        comment_addr = comment_addr0 + str(n) + ".txt"
        
        # 首页评论
        comment_list, next_page, date_nodes = get_comment(html)
        
        with open(comment_addr, 'a', encoding='utf-8') as f:
            # 写首页评论到文件
            write_comment(f, comment_list,date_nodes)
        
            while (next_page != None):  #查看“下一页”的A标签链接
                
                # 爬非评论首页的评论
                html = requests.get(next_url1 + next_page, cookies=cookies, headers=header).content
                comment_list, next_page, date_nodes = get_comment(html)
                
                # 写非评论首页的评论
                write_comment(f, comment_list, date_nodes)
                
                time.sleep(1 + float(random.randint(1, 100)) / 20)
                
            f.close()
            
    print ("Done!")