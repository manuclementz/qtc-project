from django.db import models
from django.utils import timezone
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD
import os
import shortuuid
from PIL import Image
import io
from django.core.files.base import ContentFile

def upload_path(instance, filename):
    fname, ext = os.path.splitext(filename)
    new_filename = f"{shortuuid.uuid()}.webp"
    return f"qtc/{new_filename}"

def process_image(image_field):
    if image_field and image_field.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        img = Image.open(image_field)
        img = img.convert('RGB')
        output = io.BytesIO()
        img.save(output, format='WEBP', quality=85)
        output.seek(0)
        return ContentFile(output.getvalue(), name=os.path.splitext(image_field.name)[0] + '.webp')
    return image_field


class Quiz(models.Model):
    def upload_path(self, filename):
        fname, ext = os.path.splitext(filename)
        return f"qtc/{shortuuid.uuid()}.webp"

    quiz_url_id = models.SlugField('Quiz ID', unique=True, max_length=50)
    quiz_title = models.CharField(max_length=100)
    quiz_description = MarkdownField(rendered_field='quiz_description_rendered', validator=VALIDATOR_STANDARD, null=True)
    quiz_description_rendered = RenderedMarkdownField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    quiz_media = models.FileField(upload_to=upload_path, null=True)
    squarish_images = models.BooleanField(null=True)

    @property
    def is_running(self):
        return self.start_datetime < timezone.now() < self.end_datetime

    def __str__(self):
        return self.quiz_title

    def save(self, *args, **kwargs):
        if self.quiz_media:
            self.quiz_media = process_image(self.quiz_media)
        super().save(*args, **kwargs)

    def convert_to_webp(self, file):
        image = Image.open(file)
        output = io.BytesIO()
        image.save(output, format='WEBP')
        output.seek(0)
        return output

class Question(models.Model):
    class QuestionType(models.TextChoices):
        IMAGE = 'IMG', 'Image'
        AUDIO = 'AUD', 'Audio'
        VIDEO = 'VID', 'Video'
        TEXT = 'TXT', 'Text'

    def upload_path(self, filename):
        fname, ext = os.path.splitext(filename)
        return f"qtc/{shortuuid.uuid()}.webp"

    type = models.CharField(max_length=3, choices=QuestionType.choices, default=QuestionType.IMAGE)
    file = models.FileField(upload_to=upload_path)
    question_text = models.CharField(max_length=200, blank=True)
    answer = models.CharField(max_length=200, blank=True)
    quiz = models.ForeignKey(Quiz, models.CASCADE, related_name='questions')
    question_order = models.PositiveIntegerField()

    class Meta:
        ordering = ['question_order']

    def __str__(self):
        return f"{self.question_order} - {self.question_text}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file = process_image(self.file)
        super().save(*args, **kwargs)

    def convert_to_webp(self, file):
        image = Image.open(file)
        output = io.BytesIO()
        image.save(output, format='WEBP')
        output.seek(0)
        return output

class QuizEntry(models.Model):
    unique_id = models.CharField(max_length=100)
    player_name = models.CharField(max_length=100)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='entries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"({self.quiz.quiz_title}) {self.player_name} - {self.total_score()} "
    
    def total_score(self):
        s = 0
        for a in self.entry_answers.all():
            s += a.score
        return s

class QuizEntryAnswer(models.Model):
    answer_text = models.CharField(max_length=100)
    score = models.FloatField(default=0, null=True)
    question = models.ForeignKey(Question, models.CASCADE, related_name='question_answers')
    entry = models.ForeignKey(QuizEntry, models.CASCADE, related_name='entry_answers')
    def __str__(self):
        return f"{self.entry.player_name} - {self.question.question_order} {self.question.question_text}"
