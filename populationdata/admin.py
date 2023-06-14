from django.contrib import admin
from import_export import resources
from populationdata.models import WeiboContent, WeiboContentIndex, QuestionAnswerKB, QuestionIndex
from import_export.admin import ImportExportModelAdmin

# Register your models here.
class WeiboResource(resources.ModelResource):
    class Meta:
        model = WeiboContent
        export_order = ('blogger_name','blogger_home','weibo_content')

@admin.register(WeiboContent)
class WeiboAdmin(ImportExportModelAdmin):
    list_display = ('blogger_name','blogger_home','weibo_content')
    search_fields = ('blogger_name','weibo_content')
    resource_class = WeiboResource

class WeiboIndexResource(resources.ModelResource):
    class Meta:
        model = WeiboContentIndex
        export_order = ('blogger_keyword','blogger_doclist')

@admin.register(WeiboContentIndex)
class WeiboIndexAdmin(ImportExportModelAdmin):
    list_display = ('blogger_keyword','blogger_doclist')
    search_field = ('blogger_keyword')
    resource_class = WeiboIndexResource

class QuestionAnswerResource(resources.ModelResource):
    class Meta:
        model = QuestionAnswerKB
        export_order = ('question','answer')

@admin.register(QuestionAnswerKB)
class MQuestionAnswerAdmin(ImportExportModelAdmin):
    list_display = ('question','answer')
    search_field = ('question')
    resource_class = QuestionAnswerResource

class QuestionIndexResource(resources.ModelResource):
    class Meta:
        model = QuestionIndex
        export_order = ('question_keyword','question_doclist')

@admin.register(QuestionIndex)
class QuestionIndexAdmin(ImportExportModelAdmin):
    list_display = ('question_keyword','question_doclist')
    search_field = ('question_keyword')
    resource_class = QuestionIndexResource