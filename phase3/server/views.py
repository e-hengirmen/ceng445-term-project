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
user_to_board_ID={}

# Done
@login_required
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



@login_required
def join(request):
    username = request.user.username
    if username in user_to_board_ID:
        return HttpResponse(f"already in game {user_to_board_ID[username]}")
    if "game_list_join" in request.POST:
        ID=int(request.POST["game_list_join"])
        monopoly=board_dict[ID]

        if monopoly.attach(username):
            user_to_board_ID[username]=ID
            return redirect('play')
        return redirect('/server')

    if "game_list_observe" in request.POST:
        # monopoly=board_dict[request.POST["game_list_observe"]]
        monopoly=board_dict[request.POST["game_list_observe"]]
        print(username)
        username = request.user.username
        monopoly.attach_observer(username)
        return redirect('play')
    return redirect('/server')



@login_required
def list_server(request):
    
    to_be_deleted=[]
    for game in GAME.objects.all():
        if game.game_id not in board_dict:
            to_be_deleted.append(game.game_id)
    for id in to_be_deleted:
        GAME.objects.get(game_id=id).delete()



    representation=[board_dict[game.game_id].__repr__() for game in GAME.objects.all()]
    states=        [not board_dict[game.game_id].WaitingState for game in GAME.objects.all()]
    return render(request, 'server/home.html', {"id_n_repr":zip(GAME.objects.all(),representation,states)})

# def index(request):
#     return render(request, 'home.html')

@login_required
def play(request):
    username = request.user.username
    context={"username":username}
    if username in user_to_board_ID:
        context["game_id"]=user_to_board_ID[username]
        monopoly=board_dict[context["game_id"]]
        context["waitingState"]=monopoly.WaitingState
        if context["waitingState"]:
            context["userReadyState"]=monopoly.user_dict[username]["ready"]
        else:
            context["current_user"]=monopoly.whose_turn_is_it()
    else:
        context["game_id"]="None"
    return render(request, 'server/play.html',context)


@login_required
def game_action(request):
    username = request.user.username
    context={"username":username}
    if username in user_to_board_ID:
        game_id=user_to_board_ID[username]
        monopoly=board_dict[game_id]

        command=request.POST["command"]
        if(command=="ready"):
            monopoly.ready(username)
        elif(command=="exit"):
            if(monopoly.WaitingState):
                monopoly.removeUser(username)
                del user_to_board_ID[username]
                redirect('/server')
            else:
                monopoly.turn(username,command)
                del user_to_board_ID[username]
                redirect('/server')
        else:
            monopoly.turn(username,command)

    return redirect('/server/play')
    