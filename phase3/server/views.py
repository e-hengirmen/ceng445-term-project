from django.shortcuts import render

# Create your views here.
def list_server(request):
    return render(request, 'list.html')
