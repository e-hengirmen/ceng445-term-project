from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.ServerView.as_view()),
    path('addgame/', views.addgame, name="addgame"),
    path('join/', views.join, name="join"),
]
