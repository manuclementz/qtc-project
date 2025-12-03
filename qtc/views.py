from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.http import HttpResponseNotFound
from django.urls import reverse
from .models import Quiz, QuizEntry, QuizEntryAnswer
import shortuuid
from django.views.decorators.http import require_POST, require_GET
from django.utils.html import strip_tags
from django.utils import timezone
import random
import datetime

backgrounds = ["img/darkstalkers_stage.gif", "img/lastblade_snowy_stage.gif", "img/sf3_stage_snowy_ny.gif"]            

def qtc_home(request):
    current_datetime = timezone.now()
    quiz = Quiz.objects.filter(
        start_datetime__lte=current_datetime, 
        end_datetime__gte=current_datetime,
        is_published = True
    ).first()
    if not quiz:
        return render(request, 'no-qtc.html', context = { 'background_img_url': random.choice(backgrounds)} )
    return redirect('qtc_view', quizid=quiz.quiz_url_id)


def qtc_view(request, quizid):
    quiz = Quiz.objects.filter(quiz_url_id=quizid, is_published=True).first()
    if quiz is None:
        return redirect('qtc_home')
    session_entry = request.session.get(f'qtc-{quiz.pk}')
    if session_entry:
        return redirect('qtc_view_entry', quizid=quizid, entryid=session_entry)
    blank_entry = QuizEntry(quiz=quiz)
    blank_entry.unique_id = shortuuid.uuid()
    blank_entry.save()
    for q in quiz.questions.all():
        answer = QuizEntryAnswer(question=q, entry=blank_entry)
        answer.save()
        blank_entry.entry_answers.add(answer)
    blank_entry.save()
    request.session[f'qtc-{quiz.pk}'] = blank_entry.unique_id
    request.session.set_expiry(3600*24*30)
    return redirect('qtc_view_entry', quizid=quizid, entryid=blank_entry.unique_id,)

@require_GET
def qtc_view_entry(request, quizid, entryid):
    quiz = Quiz.objects.get(quiz_url_id=quizid)
    display_options = {}
    if quiz is None:
        return HttpResponseNotFound()
    
    if quizid == 'hs-deck-the-halls' or ('special' in request.GET and request.GET['special']):
        display_options['special'] = True
        display_options['base_template'] = 'base-alt.html' 
    else:
        display_options['base_template'] = 'base.html' 
    request.session[f'qtc-{quiz.pk}'] = entryid
    request.session.set_expiry(3600*24*30)
    entry = QuizEntry.objects.get(unique_id=entryid)
    current_day = datetime.datetime.today().day
    
    return render(request, 'qtc.html', {'quiz': quiz, 'entry': entry, 'display_options':display_options, 'background_img_url': random.choice(backgrounds), 'current_day':current_day} )

@require_POST
def qtc_save_entry(request, quizid, entryid):
    for item in request.POST:
        if item.startswith('answer-'):
            answer_id = int(item.split('-')[1])
            answer = request.POST.get(item)
            entry_answer = QuizEntryAnswer.objects.get(pk=answer_id)
            entry_answer.answer_text = strip_tags(answer)
            entry_answer.save()
    user = request.POST.get('player_name')
    entry = QuizEntry.objects.get(unique_id=entryid)
    entry.player_name = user
    entry.save()
    return render(request, 'qtc-save-response.html', {'entryurl':request.build_absolute_uri(reverse('qtc_view_entry', args=(quizid, entryid)))})
