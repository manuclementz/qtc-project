from django.contrib import admin
from .models import *
from adminsortable2.admin import SortableAdminBase, SortableStackedInline, SortableTabularInline
import csv  # <--- ADD THIS IMPORT
from django.http import HttpResponse  # <--- ADD THIS IMPORT


def export_as_csv(modeladmin, request, queryset):
    """
    Admin action to export selected QuizEntry objects as a CSV file.
    """
    # Use the quiz title for the filename if only one quiz is selected
    quiz_ids = queryset.values_list('quiz__id', flat=True).distinct()
    quiz_title = "multiple-quizzes"
    if len(quiz_ids) == 1:
        try:
            quiz_title = Quiz.objects.get(pk=quiz_ids[0]).quiz_title.replace(" ", "_")
        except Quiz.DoesNotExist:
            quiz_title = "quiz"

    filename = f"quiz_entries_{quiz_title}.csv"
    
    # Create the HttpResponse object with CSV headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(u'\ufeff'.encode('utf8')) # Add BOM for Excel compatibility

    writer = csv.writer(response)
    
    # Write the CSV header row
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

    for entry in queryset.order_by('created_at'):
        answers = entry.entry_answers.all().order_by('question__question_order')
        
        for ans in answers:
            writer.writerow([
                entry.quiz.quiz_title,
                entry.player_name,
                entry.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                ans.question.question_order,
                ans.question.question_text,
                ans.answer_text,
                ans.question.answer,  # The correct answer stored on the Question model
                ans.score
            ])
            
    return response

export_as_csv.short_description = "Export Selected Entries as CSV"

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
    actions = [export_as_csv]  

admin.site.register(QuizEntryAnswer)