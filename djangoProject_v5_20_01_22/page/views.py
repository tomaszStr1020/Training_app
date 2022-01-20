from django.shortcuts import render
from django.http import HttpResponse
from djangoProject.settings import get_table, get_cursor
from django.contrib.auth import logout, get_user
from django.contrib.auth.models import User
from django_datatables_view import *
from django.views import generic
import cx_Oracle

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


def detail_group_view(request, id, *args, **kwargs):
    grupy = get_table('grupy', condition="id_grupy =" + str(id) + "")
    grupy=grupy[0]
    zawodnicy = get_table('zawodnicy')
    zawod = [a[1:3] for a in zawodnicy if a[6]==int(id)]
    trenerzy=get_table('trenerzy', condition="id_trenera =" + str(grupy[2]) + "")
    trener=trenerzy[0][1]+' '+trenerzy[0][2]
    grupy=((grupy[0], grupy[1], trener, grupy[3]))
    l=len(zawod)
    group_context = {
        'details': grupy,
        'zawodnicy': zawod,
        'l': l
    }
    return render(request, 'grupa_szczegolowe.html', group_context)

def competitor_view(request, *args, **kwargs):
    zawodnicy = get_table('zawodnicy')
    competitor_context = {
        "zawodnicy": zawodnicy
    }
    return render(request, 'zawodnicy.html', competitor_context)

def detail_competitor_view(request, id, *args, **kwargs):
    zawodnicy = get_table('zawodnicy', condition="id_zawodnika ="+str(id)+"")
    zawodnicy=zawodnicy[0]
    dysc=get_table('uprawiaja', condition="zawodnik ="+str(id)+"")
    data_ur='a'
    if (zawodnicy[4] is not None):
        data = str(zawodnicy[4])
        data_ur = data.split(' ')[0]
        rok = data_ur.split('-')[0]
        miesiac = data_ur.split('-')[1]
        dzien = data_ur.split('-')[2]
        if (dzien[0] == '0'): dzien = dzien[1]
        if (miesiac == '01'):
            mie = 'Stycznia'
        elif (miesiac == '02'):
            mie = 'Lutego'
        elif (miesiac == '03'):
            mie = 'Marca'
        elif (miesiac == '04'):
            mie = 'Kwietnia'
        elif (miesiac == '05'):
            mie = 'Maja'
        elif (miesiac == '06'):
            mie = 'Czerwca'
        elif (miesiac == '07'):
            mie = 'Lipca'
        elif (miesiac == '08'):
            mie = 'Sierpnia'
        elif (miesiac == '09'):
            mie = 'Września'
        elif (miesiac == '10'):
            mie = 'Października'
        elif (miesiac == '11'):
            mie = 'Listopada'
        elif (miesiac == '12'):
            mie = 'Grudnia'

        data_ur = str(dzien) + ' ' + str(mie) + ' ' + str(rok)
    l=len(dysc)
    detailcompetitor_context = {
        'dysc': dysc,
        'zawodnicy': zawodnicy,
        'data': data_ur,
        'l': l
    }
    return render(request, 'zawodnicy_szczegolowe.html', detailcompetitor_context)

def coach_view(request, nazwisko = None, id = None, sbmt = None, *args, **kwargs):
    trenerzy = get_table('trenerzy')
    print(nazwisko, args)
    if nazwisko and not id:
        selected = [a for a in trenerzy if a[2] == nazwisko]
        trenerzy = selected

    elif id and not nazwisko:
        selected = [a for a in trenerzy if a[0] == id]
        trenerzy = selected
    elif id and nazwisko:
        selected = [a for a in trenerzy if a[2] == nazwisko]
        selected2 = [a for a in selected if a[0] == id]
        trenerzy = selected2

    coach_context = {
        "trenerzy": trenerzy
    }
    return render(request, 'trenerzy.html', coach_context)


def detail_coach_view(request, id, *args, **kwargs):
    trenerzy = get_table('trenerzy', condition="id_trenera ="+str(id)+"")
    trenerzy=trenerzy[0]
    dysc=get_table('szkola', condition="trener ="+str(id)+"")
    data_ur='a'
    if(trenerzy[4] is not None):
        data=str(trenerzy[4])
        data_ur = data.split(' ')[0]
        rok = data_ur.split('-')[0]
        miesiac = data_ur.split('-')[1]
        dzien = data_ur.split('-')[2]
        if (dzien[0] == '0'): dzien = dzien[1]
        if (miesiac == '01'):
            mie = 'Stycznia'
        elif (miesiac == '02'):
            mie = 'Lutego'
        elif (miesiac == '03'):
            mie = 'Marca'
        elif (miesiac == '04'):
            mie = 'Kwietnia'
        elif (miesiac == '05'):
            mie = 'Maja'
        elif (miesiac == '06'):
            mie = 'Czerwca'
        elif (miesiac == '07'):
            mie = 'Lipca'
        elif (miesiac == '08'):
            mie = 'Sierpnia'
        elif (miesiac == '09'):
            mie = 'Września'
        elif (miesiac == '10'):
            mie = 'Października'
        elif (miesiac == '11'):
            mie = 'Listopada'
        elif (miesiac == '12'):
            mie = 'Grudnia'

        data_ur = str(dzien) + ' ' + str(mie) + ' ' + str(rok)
    l=len(dysc)
    detailcoach_context = {
        'dysc': dysc,
        'trenerzy': trenerzy,
        'data': data_ur,
        'l': l
    }
    return render(request, 'trenerzy_szczegolowe.html', detailcoach_context)


def plan_view(request, *args, **kwargs):
    plany = get_table('plany_treningowe')
    usrnm = User.get_username(request.user)
    name = usrnm.split('_')[0][1:]
    autorzy = get_table("trenerzy", condition=" imie in ('"+ name+"')")
    moje_plany = [a for a in plany if a[1] == autorzy[0][0]]
    plany1=[]
    mplany=[]
    for p in plany:
        autor=get_table("trenerzy", condition=" id_trenera ="+str(p[1])+"")
        a=str(autor[0][1])+' '+str(autor[0][2])
        plany1.append((p[0], a, p[2]))
    for mp in moje_plany:
        autor=get_table("trenerzy", condition=" id_trenera ="+ str(p[1])+"")
        a=str(autor[0][1])+' '+str(autor[0][2])
        mplany.append((p[0], a, p[2]))

    plany_context= {
        "moje_plany": mplany,
        "plany" : plany1,
    }

    return render(request, 'plany.html', plany_context)

def detail_plan_view(request, id, *args, **kwargs):
    plan = get_table('plany_treningowe', condition="id_planu =" + str(id) + "")[0]
    trenerzy=get_table('trenerzy', condition="id_trenera =" + str(plan[1]) + "")[0]
    autor=trenerzy[1]+' '+trenerzy[2]
    plan_context = {
        'plan': plan,
        'autor': autor
    }
    return render(request, 'plan_szczegolowe.html', plan_context)


def diet_view(request, *args, **kwargs):
    diety = get_table('diety')
    diet_context = {
        "diety": diety
    }
    return render(request, 'diety.html', diet_context)

def discipline_view(request, *args, **kwargs):
    dyscypliny = get_table('dyscypliny')
    discipline_context = {
        "dyscypliny": dyscypliny
    }
    return render(request, 'dyscypliny.html', discipline_context)

def typedisc_view(request, *args, **kwargs):
    typy = get_table('typy_dyscyplin')
    typedisc_context = {
        "typy": typy
    }
    return render(request, 'typy.html', typedisc_context)

def profile_view(request, *args, **kwargs):
    usrnm = User.get_username(request.user)
    function=usrnm[0]
    if(function=='T'):
        tabela = get_table('trenerzy')
        funkcja='Profil trenera'
    elif(function=='Z'):
        tabela = get_table('zawodnicy')
        funkcja='Profil zawodnika'
    imie=tabela[0][1]
    nazwisko=tabela[0][2]
    pesel=tabela[0][3]
    data_ur=tabela[0][4]
    data_ur=str(data_ur)
    data_ur=data_ur.split(' ')[0]
    rok=data_ur.split('-')[0]
    miesiac=data_ur.split('-')[1]
    dzien=data_ur.split('-')[2]
    if(dzien[0]=='0'):dzien=dzien[1]
    if(miesiac == '01'): mie = 'Stycznia'
    elif(miesiac == '02'): mie = 'Lutego'
    elif (miesiac == '03'): mie = 'Marca'
    elif (miesiac == '04'): mie = 'Kwietnia'
    elif (miesiac == '05'): mie = 'Maja'
    elif (miesiac == '06'): mie = 'Czerwca'
    elif (miesiac == '07'): mie = 'Lipca'
    elif (miesiac == '08'): mie = 'Sierpnia'
    elif (miesiac == '09'): mie = 'Września'
    elif (miesiac == '10'): mie = 'Października'
    elif (miesiac == '11'): mie = 'Listopada'
    elif (miesiac == '12'): mie = 'Grudnia'

    data_ur=str(dzien)+' '+str(mie)+' '+str(rok)
    profile_context = {
        "imie": imie,
        "nazwisko": nazwisko,
        "pesel": pesel,
        "data_ur": data_ur,
        "funkcja": funkcja
    }
    return render(request, 'profil.html', profile_context)


def usuwanie(request, id, typ, *args, **kwargs):
    kursor = get_cursor()
    id = int(id)
    if typ == 'dieta':
        try:
            kursor.execute('delete from diety where id_diety = '+str(id))
            print('pomyslnie usunieta dieta o id ', id)
            return render(request, 'usuniete.html')

        except:
            print('Blad usuwanie')
    elif typ == 'zawodnicy':
        try:
            kursor.callproc("UsunZawodnika", [id])
            print('Pomyslnie usuniety zaowdnik')
            return render(request, 'usuniete.html')
        except:
            print('Blad usuwania zawodnika')

    return render(request, 'usuniete.html')


#Obługa błędów
def ErrorView(request, *args, **kwargs):
    return HttpResponse("Błąd połączenia")

def logout_view(request):
    logout(request)
    return home_view(request, 'home_view')