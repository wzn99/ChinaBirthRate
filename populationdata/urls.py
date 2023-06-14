from django.urls import re_path as url
from populationdata import views

urlpatterns = [
    url(r'^populationdata', views.populationData, name='populationData'),
    url(r'^buildindex', views.buildindex, name='buildIndex'),
    url(r'^buildquestionindex', views.buildindex, name='buildquestionIndex'),
    url(r'^searchindex', views.searchindex, name='searchIndex'),
    url(r'^weiboClassification', views.weiboClassification, name='weiboClassification'),
    url(r'^questionAnswering',views.questionAnswering,name='questionAnswering'),
    url(r'^searchanswer', views.searchanswer, name= 'searchAnswer'),
    url(r'^posannotation', views.posannotation, name='posAnnotation'),
    url(r'^nerannotation', views.nerannotation,name='nerAnnotation')
]
