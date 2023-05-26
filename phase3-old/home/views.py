from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login
from django.urls import path, include


# from django.shortcuts import render
from django.views import View
from django.conf import settings

# Create your views here.

# This is a little complex because we need to detect when we are
# running in various configurations


class HomeView(View):
    context = {}
    def get(self, request):
        return render(request, 'home.html')
    

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/server')  # Redirect to the home page after successful login
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

