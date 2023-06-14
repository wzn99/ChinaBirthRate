from django.db import models

# Create your models here.
class WeiboContent(models.Model):
    blogger_name = models.CharField(max_length=256)
    blogger_home = models.CharField(max_length=64)
    weibo_content = models.TextField()
    def __str__(self):
        return self.blogger_name

# 创建索引表
class WeiboContentIndex(models.Model):
    blogger_keyword = models.CharField(max_length=256)
    blogger_doclist = models.TextField()
    def __str__(self):
        return self.blogger_keyword
    
# 创建问答知识库表
class QuestionAnswerKB(models.Model):
    question = models.TextField()
    answer = models.TextField()
    def __str__(self):
        return self.question

# 创建问题索引表
class QuestionIndex(models.Model):
    question_keyword = models.CharField(max_length=256)
    question_doclist = models.TextField()
    def __str__(self):
        return self.question_keyword