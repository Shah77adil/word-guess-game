# game/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.start_game, name='start_game'),
    path('guess/', views.guess_letter, name='guess_letter'),
]
