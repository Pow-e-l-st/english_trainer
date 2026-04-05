"""Маршруты (URL) приложения trainer."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cards/', views.card_list, name='card_list'),
    path('cards/create/', views.card_create, name='card_create'),
    path('cards/<int:pk>/edit/', views.card_edit, name='card_edit'),
    path('cards/<int:pk>/delete/', views.card_delete, name='card_delete'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/edit/', views.assignment_edit, name='assignment_edit'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
    path('assignments/<int:pk>/practice/<str:direction>/',
         views.practice_assignment, name='practice_assignment'),
    path('random/', views.practice_random, name='random_assignment'),
    path('random/practice/', views.practice_random_session, name='practice_random_session'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
]