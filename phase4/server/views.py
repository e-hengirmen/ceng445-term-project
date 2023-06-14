from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login


# from django.shortcuts import render
from django.views import View
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


from Board import Board
from Server import Server

#---------------globals--------------------
user_to_board_ID={}
user_svg_dict={}

server=Server()

#------------------------------------------

# Done
@login_required
def addgame(request):
    if "choice" in request.POST:
        user_count = request.POST.get('choice')
        message="choose a number"
        if user_count!="None":
            message=f"Game added with {user_count}"
            
            server.new(int(user_count))

        # return render(request, 'server/home.html', {"games":GAME.objects.all(),"message":message})
    return redirect('/server')



@login_required
def join(request):
    username = request.user.username
    if username in user_to_board_ID:
        return HttpResponse(f"already in game {user_to_board_ID[username]}")
    if "game_list_join" in request.POST:
        ID=int(request.POST["game_list_join"])

        user_svg_dict[ID]={}

        # if monopoly.attach(username):
        if server.open_with_ID(ID,username):
            user_to_board_ID[username]=ID
            return redirect('play')
        return redirect('/server')

    if "game_list_observe" in request.POST:
        if username in user_to_board_ID:
            return HttpResponse(f"already in game {user_to_board_ID[username]}")
        ID=int(request.POST["game_list_observe"])
        
        # monopoly=server.game_dict[ID]
        # monopoly.attach_observer(username)
        if server.observe_with_ID(ID,username):
            user_to_board_ID[username]=ID
            return redirect('play')
        return redirect('/server')
    return redirect('/server')



@login_required
def list_server(request):
    context={"username":request.user.username}
    return render(request, 'server/home.html',context)

    game_dict1=server.list()

    game_dict={}
    for key,value in game_dict1.items():
        if None==value.winner:
            game_dict[key]=value
        else:
            print(value.winner,"---------")


    game_id_list=list(game_dict.keys())
    representation=[game_dict[game_id].__repr__() for game_id in game_id_list]
    states=        [not game_dict[game_id].WaitingState for game_id in game_id_list]
    return render(request, 'server/home.html', {"id_n_repr":zip(game_id_list,representation,states)})

# def index(request):
#     return render(request, 'home.html')

@login_required
def play(request):
    username = request.user.username
    context={"username":username}
    if username in user_to_board_ID:
        context["game_id"]=user_to_board_ID[username]
        game_id=context["game_id"]
        monopoly=server.list()[context["game_id"]]

        if monopoly.game_has_ended:
            context["winner"]=monopoly.winner
        context["states"] = monopoly.cells
        context["user_states"] = monopoly.user_dict
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
            user_svg_dict[game_id][username] = user_svg
        context['user_svg_dict']=user_svg_dict[game_id]

        # property svg
        i=0
        for cell in context["states"]:
            if cell['type'] == 'property':
                cell['owner'] = cell['property'].owner
                cell['level'] = cell['property'].level
                cell['y_position'] = i*50
                i+=1








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
        monopoly=server.list()[game_id]

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
                # if monopoly.game_has_ended:
                    # server.game_is_over(game_id)
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
    