from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.list_server, name="server"),
    path('addgame/', views.addgame, name="addgame"),
    path('join/', views.join, name="join"),

    path('play/', views.play, name="play"),
    path('game_action/', views.game_action, name="game_action"),
]
