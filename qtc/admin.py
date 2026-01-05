from django.contrib import admin
from .models import *
from adminsortable2.admin import SortableAdminBase, SortableStackedInline, SortableTabularInline
import csv
from django.http import HttpResponse

def export_quiz_results_csv(modeladmin, request, queryset):
    """
    Export all player answers for the selected quizzes.
    Filters out entries with empty player names.
    """
    filename = "quizzes_export.csv"
    if queryset.count() == 1:
        filename = f"export_{queryset.first().quiz_title.replace(' ', '_')}.csv"

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(u'\ufeff'.encode('utf8')) # Excel UTF-8 BOM

    writer = csv.writer(response)
    
    # Write Header
    writer.writerow([
        'Quiz Title', 
        'Player Name', 
        'Entry Created At',
        'Question Order', 
        'Question Text', 
        'Submitted Answer', 
        'Correct Answer', 
        'Score'
    ])

    # Loop through selected Quizzes
    for quiz in queryset:
        # Fetch entries for this quiz, exclude empty player names, and optimize DB hits
        entries = quiz.entries.exclude(player_name__isnull=True).exclude(player_name__exact='') \
                              .prefetch_related('entry_answers__question') \
                              .order_by('created_at')

        for entry in entries:
            # Final safety check for whitespace-only names
            if not entry.player_name.strip():
                continue

            for ans in entry.entry_answers.all():
                writer.writerow([
                    quiz.quiz_title,
                    entry.player_name,
                    entry.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    ans.question.question_order,
                    ans.question.question_text,
                    ans.answer_text,
                    ans.question.answer,
                    ans.score
                ])
                
    return response

export_quiz_results_csv.short_description = "Export All Answers for Selected Quizzes"

class QuestionAdmin(SortableTabularInline):
    model = Question

@admin.register(Quiz)
class QuizAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = [QuestionAdmin]
    actions = [export_quiz_results_csv]  # <--- Added action here

class QuizEntryAnswerAdmin(admin.TabularInline):
    model = QuizEntryAnswer
    readonly_fields = ['question', 'answer_text']

@admin.register(QuizEntry)
class QuizEntryAdmin(admin.ModelAdmin):
    inlines = [QuizEntryAnswerAdmin]
    list_filter = ["quiz__quiz_title"]
    # You can keep the action here too if you want to export specific entries
    actions = [export_quiz_results_csv]  

admin.site.register(QuizEntryAnswer)