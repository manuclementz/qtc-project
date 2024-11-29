from django.contrib import admin
from .models import *
from adminsortable2.admin import SortableAdminBase, SortableStackedInline, SortableTabularInline


class QuestionAdmin(SortableTabularInline):
    model = Question

@admin.register(Quiz)
class QuizAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = [QuestionAdmin]

class QuizEntryAnswerAdmin(admin.TabularInline):
    model = QuizEntryAnswer
    readonly_fields = ['question', 'answer_text']
    

@admin.register(QuizEntry)
class QuizEntryAdmin(admin.ModelAdmin):
    inlines = [QuizEntryAnswerAdmin]
    list_filter = ["quiz__quiz_title"]

admin.site.register(QuizEntryAnswer)