from django.urls import path
from . import views
from server.views import ServerView
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include

urlpatterns = [
    path('', views.HomeView.as_view()),
    # path('login/', LoginView.as_view(template_name='login.html'), name='login'), 
    path('login/', views.user_login, name='login'), 
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),

]
