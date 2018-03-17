# -*- coding: utf-8 -*-

'''
用逆向最大匹配法分词
'''

import re
from openpyxl import Workbook 

# -*- 读取待分词文本，返回存储有该文件内容行内容的列表 -*-
# 思路：打开评论文件：
#        如果文件打开失败则告警；
#        如果文件打开成功：
#           1、顺序读取文章中的每一个句子；
#           2、对句子进行处理，删除句子中的空格；
#           3、用句号取代句子中可能有英文标点符号；
#           4、将处理后的句子存入列表；
#        文件读取完成后，返回存储有处理好的句子的列表。
def read_file(raw_file_path):
    try:
        file_comments = open(raw_file_path, "r")
    except IOError, e:
        print "open file--", raw_file_path, "--error!:", e
    
    else:
        raw_file = []
        for eachlines in file_comments.readlines():
                # 处理空格和英文标点符号
                eachlines = eachlines.replace(" ","").replace("\t","").strip() 
                eachlines = re.sub("[\#,.+~?\-:;'\"!`]|(-{2})|(\.{3})|(\(\))|(\[\])|({})","。", eachlines)
                raw_file.append(eachlines)
        file_comments.close()
        return raw_file
        
# -*- 读取分词词典，返回存有所有单词的列表 -*-
def read_dic(dic_path):
    try:
        file_dic = open(dic_path, "r")
    except IOError, e:
        print "open file--", dic_path, "--error!:", e

    else:
        dic = []
        raw_file = file_dic.readlines()
        for eachlines in raw_file:
            dic.append(eachlines.strip())
        file_dic.close()
        return dic


# -*- 逆向最大匹配法分词 -*-
# 思路：1、找到文章最大词长，以此为起始比对句子内容；
#      2、从文章拿出每一行的句子；
#           2-1、去除空白内容，准备比对；
#           2-2、将句子长度与最长词长比对，如果超出句子长度，将上限调整为句子的长度；
#      3、循环判断，从句子后面取出当前长度的字符，查看是否在词典中；
#           3-1、如果在词典中，那么就存入list；
#           3=2、否则，直到比较长度到达1才存入list；
#      4、比对完毕，按顺序输出。
def cut_words(raw_sentences, word_dic):
    
    lines = 1
    word_cut = []
    max_length = max(len(word) for word in word_dic)

    for sentence in raw_sentences:

        sentence = sentence.strip()
        print(sentence)
        words_length = len(sentence)
        cut_word_list = []
        
        while words_length > 0:

            max_cut_length = min(words_length, max_length)
            i = max_cut_length

            while (i >= 0):

                # 对字母的判断
                if sentence[words_length - 1] >= 'A' and sentence[words_length - 1] <= 'z':
                    tmp = words_length - 1
                    while (sentence[tmp] >= 'A' and sentence[tmp] <= 'z' and tmp >= 0):
                        tmp = tmp - 1
                    new_word = sentence[tmp + 1 : words_length]
                    cut_word_list.append(new_word)
                    words_length = tmp + 1
                    break
                    
                # 对数字的判断    
                elif sentence[words_length - 1] >= '0' and sentence[words_length - 1] <= '9':
                    tmp = words_length - 1
                    while (sentence[tmp] >= '0' and sentence[tmp] <= '9' and tmp >= 0):
                        tmp = tmp - 1
                    new_word = sentence[tmp + 1 : words_length]
                    cut_word_list.append(new_word)
                    words_length = tmp + 1
                    break

                # 对中文的判断
                else:
                    new_word = sentence[words_length - i: words_length]
                    
                    if new_word in word_dic:
                        cut_word_list.append(new_word)
                        exsheet.cell(row = lines, column = 1).value = new_word
                        lines = lines + 1
                        words_length = words_length - i
                        break
                    
                    elif i <= 3:
                        cut_word_list.append(new_word)
                        words_length = words_length - 3
                        break

                    elif sentence[words_length - i] >= '0' and sentence[words_length - i] <= '9':
                        i = i - 1
                    
                    elif sentence[words_length - i] >= 'A' and sentence[words_length - i] <= 'z':
                        i = i - 1
                    
                    else:
                        i = i - 3

        cut_word_list.reverse()

        words="/".join(cut_word_list)
        word_cut.append(words.lstrip("/"))

        for sentence in word_cut:
            print(sentence)
            f.write(sentence)
            f.write("\n")
            word_cut = []


# -*- main -*-
# 读取待分词文本，输入预期处理的文本数量
total = input("Please input text number:")

# 读取词典
wordfile_path = "dic.txt"
words_dic = read_dic(wordfile_path)

# 逆向最大匹配法分词
for i in range(0, total):

    rawfile_path = "comment/" + str(i) + ".txt"
    outfile_path = "output/txts/" + str(i) + ".txt"
    outexcel_path = "output/excels/" + str(i) + ".xlsx"
    
    # 准备处理、输出文本和表格
    try:
        f = open(outfile_path, "w")
    except IOError, e:
        print "open file--", outfile_path, "--error!:", e

    # 准备导入表格
    data = Workbook()
    exsheet = data.get_active_sheet()
    
    # 读取评论内容，对文本进行分词
    raw_file = read_file(rawfile_path)
    content_cut = cut_words(raw_file, words_dic)

    data.save(filename = outexcel_path)
    f.close()