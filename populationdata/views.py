import difflib
from django.shortcuts import render
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger
from populationdata.models import WeiboContent, WeiboContentIndex, QuestionAnswerKB, QuestionIndex
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
import jieba
import re
import os
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import jieba.posseg as psg
import jieba.analyse
from django.db.models import Q
from functools import reduce

def populationData(request):
    weibo_list = WeiboContent.objects.all()
    paginator = Paginator(weibo_list, 20)
    page = request.GET.get('page')
    data_list = []
    if page:
        data_list = paginator.page(page).object_list
    else:
        data_list = paginator.page(1).object_list
    try:
        page_object = paginator.page(page)
    except PageNotAnInteger:
        page_object = paginator.page(1)
    except EmptyPage:
        page_object = paginator.page(paginator.num_pages)
    return render(request,"populationdata.html",{
        'page_object':page_object,
        'data_list':data_list
    })

# 定义索引请求链接.
@csrf_exempt
def buildindex(request):
    res = {
        'status': 404,
        'text': 'Unknown request!'
    }
    if request.method == 'POST':
        name = request.POST['id']
        if name == 'submit2index':
            # 初始化停用词列表
            # 注意：从网上下载一个较为全面完整的stopwords.txt用于本次任务。此处只是一个简单的示例文件
            stopwords = []
            static_filepath = os.path.join(settings.STATIC_ROOT, 'refs')
            file_path = os.path.join(static_filepath, 'stopwords.txt')
            for word in open(file_path, encoding='utf-8'):
                stopwords.append(word.strip())
            # 获取所有微博内容的文本属性用于索引
            weibo_list = WeiboContent.objects.values('id', 'blogger_name', 'blogger_home', 'weibo_content')
            all_keywords = []
            weibo_set = dict()
            for weibo in weibo_list:
                weibo_id = weibo['id']
                text = weibo['blogger_name']+weibo['blogger_home']+weibo['weibo_content']
                # 正则表达式去除非文字和数字的字符
                weibo_text = re.sub(r'[^\w]+', '', text.strip())
                cut_text=jieba.cut(weibo_text, cut_all=False)
                keywordlist = []
                for word in cut_text:
                    # 此处去停用词
                    if word not in stopwords:
                        keywordlist.append(word)
                all_keywords.extend(keywordlist)
                weibo_set[weibo_id] = keywordlist
            # 利用set删除重复keywords
            set_all_keywords = set(all_keywords)
            # 建立倒排索引
            for term in set_all_keywords:
                temp=[]
                for m_id in weibo_set.keys():
                    cut_text = weibo_set[m_id]
                    if term in cut_text:
                        temp.append(m_id)
                # 存储索引到数据库
                try:
                    exist_list = WeiboContentIndex.objects.get(blogger_keyword=term)
                    exist_list.blogger_doclist = json.dumps(temp)
                    exist_list.save()
                except ObjectDoesNotExist:
                    new_list = WeiboContentIndex(blogger_keyword=term, blogger_doclist=json.dumps(temp))
                    new_list.save()
            res = {
                'status': 200,
                'text': 'Index successfully!'
            }
    return HttpResponse(json.dumps(res), content_type='application/json')

# 定义检索请求链接.
def searchindex(request):
    res = {
        'status': 404,
        'text': 'Unknown request!'
    }
    if request.method == 'GET':
        name = request.GET['id']
        if name == 'submit2search':
            try:
                # 获取前端的关键词
                keyword = request.GET['keyword']
                # 精确匹配索引关键词
                # 如何实现模糊匹配？
                invertedindex_rec = WeiboContentIndex.objects.get(blogger_keyword=keyword)
                # 将文档列表字符串转化成数组
                jsonDec = json.decoder.JSONDecoder()
                result = jsonDec.decode(invertedindex_rec.blogger_doclist)
                # 查询微博ID在数组内的数据
                result_queryset = WeiboContent.objects.filter(id__in=result).values()
                if result_queryset:
                    res = {
                        'status': 200,
                        'text': list(result_queryset)
                    }
                else:
                    res = {
                        'status': 201,
                        'text': 'No result!'
                    }
            except ObjectDoesNotExist:
                res = {
                    'status': 201,
                    'text': 'No result!'
                }
    return HttpResponse(json.dumps(res), content_type='application/json')

def get_similar_questions(query, threshold=0.5):
    similar_questions = []
    # 使用jieba进行分词
    seg_list = jieba.cut(query)
    # 提取关键词列表
    keywords = [word for word in seg_list]
    # 获取匹配的索引项
    matched_indexes = QuestionIndex.objects.filter(question_keyword__in=keywords)
    # 获取匹配的问题
    matched_questions = []

    for index in matched_indexes:
        questions = QuestionAnswerKB.objects.filter(id__in=eval(QuestionIndex.objects.get(question_keyword=index.question_keyword).question_doclist))
        matched_questions.extend(list(questions))

    for qa_rec in matched_questions:
        similarity = difflib.SequenceMatcher(None, query, qa_rec.question).ratio()
        if similarity >= threshold:
            similar_questions.append((qa_rec, similarity))

    similar_questions.sort(key=lambda x: x[1], reverse=True)
    return similar_questions

# 定义问答检索请求链接.
@csrf_exempt
def searchanswer(request):
    res = {
        'status': 404,
        'text': 'Unknown request!'
    }
    if request.method == 'GET':
        name = request.GET['id']
        if name == 'chatbotsendbtn':
            try:
                # 获取前端的问题文本
                text = request.GET['text']
                # 检索问题，匹配答案
                # 近似问题检索
                similar_questions = get_similar_questions(text)
                if similar_questions:
                    answers = [qa_rec.answer for qa_rec, _ in similar_questions]
                    res = {
                        'status': 200,
                        'answer': answers[0]  # 返回相似度最高的答案
                    }
                else:
                    res = {
                        'status': 201,
                        'answer': 'No answer!'
                    }
            except ObjectDoesNotExist:
                res = {
                    'status': 201,
                    'answer': 'No answer!'
                }
            return HttpResponse(json.dumps(res), content_type='application/json')

# 定义挖掘页面.
def weiboClassification(request):
    return render(request, 'weiboClassification.html', {
        })   

# 定义词性标注请求链接.
@csrf_exempt
def posannotation(request):
    res = {
        'status': 404,
        'text': 'Unknown request!'
    }
    if request.method == 'GET':
        # 获取当前需要标注的微博id
        movie_idcur = request.GET['id']
        if movie_idcur:
            try:
                # 获取当前微博数据
                result = WeiboContent.objects.get(id=movie_idcur)
                weibo_text = result.weibo_content            
                # 词性标注代码如下
                seg_list = psg.cut(weibo_text)
                text = ''
                for word, pos in seg_list:
                    new_word = word
                    if pos == 'n':
                        new_word = '<span style="background-color: yellow;">' + word + '</span>' # yellow background
                    elif pos == 'v':
                        new_word = '<span style="background-color: green;">' + word + '</span>' # green background
                    elif pos == 'a':
                        new_word = '<span style="background-color: red;">' + word + '</span>' # green background
                    elif pos == 'ad':
                        new_word = '<span style="background-color: blue;">' + word + '</span>' # green background
                    text += new_word
                    result.weibo_content = text
                response_data = {'id': result.id,'blogger_name': result.blogger_name,'blogger_home': result.blogger_home,'weibo_content': result.weibo_content}
                if result:
                    res = {
                        'status': 200,
                        'data': response_data
                    }
                else:
                    res = {
                        'status': 201,
                        'data': 'No result!'
                    }
            except ObjectDoesNotExist:
                res = {
                    'status': 201,
                    'data': 'No result!'
                }
    return HttpResponse(json.dumps(res), content_type='application/json')

# 定义实体识别请求链接.
@csrf_exempt
def nerannotation(request):
    res = {
        'status': 404,
        'text': 'Unknown request!'
    }
    if request.method == 'GET':
        # 获取当前需要标注的微博id
        movie_idcur = request.GET['id']
        if movie_idcur:
            try:
                # 获取当前微博数据
                result = WeiboContent.objects.get(id=movie_idcur)
                weibo_text = result.weibo_content
                # 词性标注代码如下
                seg_list = psg.cut(weibo_text)
                seg_list2 = jieba.analyse.textrank(weibo_text,topK=20,withWeight=True,allowPOS=('ns','n'))
                text = ''
                for word, pos in seg_list:
                    new_word = word
                    for item1,item2 in seg_list2:
                        if new_word == item1:
                            new_word = '<span style="background-color: pink;">' + word + '</span>' # pink background
                            break
                    text += new_word
                    result.weibo_content = text
                response_data = {'id': result.id,'blogger_name': result.blogger_name,'blogger_home': result.blogger_home,'weibo_content': result.weibo_content}
                if result:
                    res = {
                        'status': 200,
                        'data': response_data
                    }
                else:
                    res = {
                        'status': 201,
                        'data': 'No result!'
                    }
            except ObjectDoesNotExist:
                res = {
                    'status': 201,
                    'data': 'No result!'
                }
    return HttpResponse(json.dumps(res), content_type='application/json')

def questionAnswering(request):
    data_list=[]
    return render(request, 'weiboQuestionAnswering.html', {
        # 'page_object': page_object,
        'data_list': data_list
    })

# 定义索引请求链接.
@csrf_exempt
def buildquestionindex(request):
    res = {
        'status': 404,
        'text': 'Unknown request!'
    }
    if request.method == 'POST':
        name = request.POST['id']
        if name == 'submit3index':
            # 初始化停用词列表
            # 注意：从网上下载一个较为全面完整的stopwords.txt用于本次任务。此处只是一个简单的示例文件
            stopwords = []
            static_filepath = os.path.join(settings.STATIC_ROOT, 'refs')
            file_path = os.path.join(static_filepath, 'stopwords.txt')
            for word in open(file_path, encoding='utf-8'):
                stopwords.append(word.strip())
            # 获取所有问答内容的文本属性用于索引
            questionAnswering_list = QuestionAnswerKB.objects.values('id', 'question', 'answer')
            all_keywords = []
            questionAnswering_set = dict()
            for questionAnswering in questionAnswering_list:
                questionAnswering_id = questionAnswering['id']
                text = questionAnswering['question']
                # 正则表达式去除非文字和数字的字符
                questionAnswering_text = re.sub(r'[^\w]+', '', text.strip())
                cut_text=jieba.cut(questionAnswering_text, cut_all=False)
                keywordlist = []
                for word in cut_text:
                    # 此处去停用词
                    if word not in stopwords:
                        keywordlist.append(word)
                all_keywords.extend(keywordlist)
                questionAnswering_set[questionAnswering_id] = keywordlist
            # 利用set删除重复keywords
            set_all_keywords = set(all_keywords)
            # 建立倒排索引
            for term in set_all_keywords:
                temp=[]
                for m_id in questionAnswering_set.keys():
                    cut_text = questionAnswering_set[m_id]
                    if term in cut_text:
                        temp.append(m_id)
                # 存储索引到数据库
                try:
                    exist_list = QuestionIndex.objects.get(question_keyword=term)
                    exist_list.question_doclist = json.dumps(temp)
                    exist_list.save()
                except ObjectDoesNotExist:
                    new_list = QuestionIndex(question_keyword=term, question_doclist=json.dumps(temp))
                    new_list.save()
            res = {
                'status': 200,
                'text': 'Index successfully!'
            }
    return HttpResponse(json.dumps(res), content_type='application/json')