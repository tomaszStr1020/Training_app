from django.shortcuts import render
from django.http import HttpResponse
from djangoProject.settings import get_table
from django.contrib.auth import logout, get_user
from django.contrib.auth.models import User

def home_view(request, *args, **kwargs):

    assert get_table("trenerzy") !=0,ErrorView(request.user)
    res = get_table("trenerzy")
    try:
        a = User.get_username(request.user)
    except:
        a= ''
    zawodnicy = {
        "kursor": res,
        "username":a

    }
    #return HttpResponse("<h1> Hello world! </h1>")
    #Dużo lepszy sposób pozwalający stworzyć dużo dłuższy kod html
    #Wszelkie pliki html wrzucamy do folderu, który musimy stworzyć templates
    #Nie zapomnij dodać ścieżki do templates w ustawieniach projektu (TEMPLATES .... DIRS [ścieżka]
    return render(request, "home.html",zawodnicy)

def group_view(request, *args, **kwargs):



    return render(request, 'grupy.html')

def contact_view(request,*args, **kwargs):
    return HttpResponse("<h1> Contact </h1>")

def about_view(request,*args, **kwargs):
    return HttpResponse("<h1> About </h1>")

def gallery_view(request,*args, **kwargs):
    return HttpResponse("<h1> Gallery </h1>")

#Obługa błędów
def ErrorView(request, *args, **kwargs):
    return HttpResponse("Błąd połączenia")

def logout_view(request):
    logout(request)
    return home_view(request, 'home_view')