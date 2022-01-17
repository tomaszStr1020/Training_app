from django.shortcuts import render
from django.http import HttpResponse
from djangoProject.settings import get_table
from django.contrib.auth import logout, get_user
from django.contrib.auth.models import User
from django_datatables_view import *
def home_view(request, *args, **kwargs):

    assert get_table("trenerzy") !=0,ErrorView(request.user)
    res = get_table("trenerzy")
    try:
        a = User.get_username(request.user)
    except:
        a= ''
    zawodnicy = {
        "kursor": res,
        "username": a

    }
    #return HttpResponse("<h1> Hello world! </h1>")
    #Dużo lepszy sposób pozwalający stworzyć dużo dłuższy kod html
    #Wszelkie pliki html wrzucamy do folderu, który musimy stworzyć templates
    #Nie zapomnij dodać ścieżki do templates w ustawieniach projektu (TEMPLATES .... DIRS [ścieżka]
    return render(request, "home.html",zawodnicy)

def group_view(request, *args, **kwargs):
    if len(args)>1:
        print(args[1])
    grupy = get_table('grupy')
    usrnm = User.get_username(request.user)
    if usrnm[0] not in ['Z', 'T']:

        return render(request, 'grupy.html',{'grupy': grupy})
    name = usrnm.split('_')[0][1:]
    print(name)
    trenerzy = get_table("trenerzy", condition=" imie in ('"+ name+"')")



    moje_grupy = [a for a in grupy if a[2] == trenerzy[0][0]]
    links = []
    print(moje_grupy)
    group_context= {
        "moje_grupy": moje_grupy,
        "grupy" : grupy,
        'iterate': 1
    }

    return render(request, 'grupy.html', group_context)


def detail_group_view(request):

    print('halolhalo')
    return render(request, 'grupa_szczegolowe.html' )
#Obługa błędów
def ErrorView(request, *args, **kwargs):
    return HttpResponse("Błąd połączenia")

def logout_view(request):
    logout(request)
    return home_view(request, 'home_view')