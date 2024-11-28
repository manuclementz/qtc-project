from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('<slug:quizid>/', views.qtc_view, name="qtc_view"),
    path('<slug:quizid>/<str:entryid>/', views.qtc_view_entry, name="qtc_view_entry"),
    path('save/<slug:quizid>/<str:entryid>/', views.qtc_save_entry, name="qtc_save_entry"),
] 