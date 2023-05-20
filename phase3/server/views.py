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

#---------------globals--------------------
board_dict={}
user_to_board_ID={}
user_svg_dict={}
#------------------------------------------

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

            monopoly=Board("gameBoards/deneme2_in",number_of_users=int(user_count))
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
        if username in user_to_board_ID:
            return HttpResponse(f"already in game {user_to_board_ID[username]}")
        ID=int(request.POST["game_list_observe"])
        
        user_to_board_ID[username]=ID
        
        monopoly=board_dict[ID]
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

        if monopoly.game_has_ended:
            context["winner"]=monopoly.winner
        context["states"] = board_dict[context["game_id"]].cells
        context["user_states"] = board_dict[context["game_id"]].user_dict
        context["colors"] = colors = {
        "red": "#FF0000",
        "blue": "#0000FF",
        }

        for i, cell in enumerate(context["states"]):
            cell['x_position'] = i * 100



        # user_svg
        user_svg = {}
        user_svg['user'] = username
        if username in monopoly.order:
            order = monopoly.order.index(username)
            user_svg['x_position'] = 100*context["user_states"][username]['position'] + order*30  + 20
            user_svg_dict[username] = user_svg
        context['user_svg_dict']=user_svg_dict

        # property svg
        for cell in board_dict[context["game_id"]].cells:
            if cell['type'] == 'property':
                cell['owner'] = cell['property'].owner
                cell['level'] = cell['property'].level








        context["waitingState"]=monopoly.WaitingState

        if username in monopoly.order:
            if context["waitingState"]:
                context["userReadyState"]=monopoly.user_dict[username]["ready"]
            else:
                context["avaliable_commands"]=monopoly.getCommands(username)
                print(context["avaliable_commands"])
        if context["waitingState"]==False:
            context["current_user"]=monopoly.whose_turn_is_it()
            context["notifications"]=monopoly.display_related_messages()
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
        print(command)
        if(command=="ready"):
            monopoly.ready(username)
        elif(command=="exit"):
            if(monopoly.game_has_ended):
                del user_to_board_ID[username]
                return redirect('/server')
            elif(monopoly.WaitingState):
                monopoly.removeUser(username)
                del user_to_board_ID[username]
                return redirect('/server')
            else:
                monopoly.turn(username,command)
                
                game_id=user_to_board_ID[username]
                del user_to_board_ID[username]
                if monopoly.game_has_ended:
                    GAME.objects.get(game_id=game_id).delete()
                return redirect('/server')
        else:
            if(command.startswith("card ")):
                command="Pick"
            if(command=="Teleport" or command=="Pick"):
                if "text_submission" in request.POST:
                    command=command+f"({request.POST['text_submission']})"
                    print(command)
            monopoly.turn(username,command)

    return redirect('/server/play')
    