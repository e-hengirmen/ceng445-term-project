from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login


# from django.shortcuts import render
from django.views import View
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


from server.models import GAME
from Board import Board

board_dict={}

def addgame(request):
    if "choice" in request.POST:
        user_count = request.POST.get('choice')
        message="choose a number"
        if user_count!="None":
            message=f"Game added with {user_count}"
            
            monopoly_model_object=GAME()
            monopoly_model_object.user_count=int(user_count)
            monopoly_model_object.save()

            monopoly=Board("gameBoards/deneme_in",number_of_users=int(user_count))
            board_dict[monopoly_model_object.game_id]=monopoly

        # return render(request, 'server/home.html', {"games":GAME.objects.all(),"message":message})
        return redirect('/server')
def join(request):
    if "game_list_join" in request.POST:
        print(request.POST["game_list_join"],"join")
        return redirect('/server')
    if "game_list_observe" in request.POST:
        print(request.POST["game_list_observe"],"observe")
        return redirect('/server')
    return redirect('/')

# @method_decorator(login_required, name='dispatch')
class ServerView(View):
    def get(self, request):
        # states=[board_dict[game.game_id].getboardstate() for game in GAME.objects.all()]
        representation=[board_dict[game.game_id].__repr__() for game in GAME.objects.all()]
        states=        [not board_dict[game.game_id].WaitingState for game in GAME.objects.all()]
        return render(request, 'server/home.html', {"id_n_repr":zip(GAME.objects.all(),representation,states)})

# def index(request):
#     return render(request, 'home.html')

