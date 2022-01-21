from django.shortcuts import render
from django.http import HttpResponse
from djangoProject.settings import get_table, get_cursor
from django.contrib.auth import logout, get_user
from django.contrib.auth.models import User
from django_datatables_view import *
from django.views import generic
from page.view_functions import *
from datetime import datetime

import cx_Oracle


def home_view(request, *args, **kwargs):
    assert get_table("trenerzy") != 0, ErrorView(request.user)
    res = get_table("trenerzy")
    try:
        a = User.get_username(request.user)
    except:
        a = ''
    zawodnicy = {
        "kursor": res,
        "username": a

    }
    # return HttpResponse("<h1> Hello world! </h1>")
    # Dużo lepszy sposób pozwalający stworzyć dużo dłuższy kod html
    # Wszelkie pliki html wrzucamy do folderu, który musimy stworzyć templates
    # Nie zapomnij dodać ścieżki do templates w ustawieniach projektu (TEMPLATES .... DIRS [ścieżka]
    return render(request, "home.html", zawodnicy)


def group_view(request, *args, **kwargs):
    if len(args) > 1:
        print(args[1])
    grupy = get_table('grupy')
    usrnm = User.get_username(request.user)
    if usrnm[0] not in ['Z', 'T']:
        return render(request, 'grupy.html', {'grupy': grupy})
    name = usrnm.split('_')[0][1:]
    print(name)
    trenerzy = get_table("trenerzy", condition=" imie in ('" + name + "')")

    moje_grupy = [a for a in grupy if a[2] == trenerzy[0][0]]
    links = []
    print(moje_grupy)
    group_context = {
        "moje_grupy": moje_grupy,
        "grupy": grupy,
        'iterate': 1
    }

    return render(request, 'grupy.html', group_context)


def detail_group_view(request, id, *args, **kwargs):
    grupy = get_table('grupy', condition="id_grupy =" + str(id) + "")
    grupy=grupy[0]
    usrnm = User.get_username(request.user)
    name = usrnm.split('_')[0][1:]
    zawodnicy = get_table('zawodnicy')
    zawod = [a[1:3] for a in zawodnicy if a[6]==int(id)]
    trenerzy=get_table('trenerzy', condition="id_trenera =" + str(grupy[2]) + "")
    mg=0
    if(name==trenerzy[0][1]):
        mg=1
    trener=trenerzy[0][1]+' '+trenerzy[0][2]
    grupy=((grupy[0], grupy[1], trener, grupy[3]))
    l=len(zawod)
    group_context = {
        'details': grupy,
        'zawodnicy': zawod,
        'l': l,
        'mg': mg,
        'id': id
    }
    return render(request, 'grupa_szczegolowe.html', group_context)


def add_group_view(request, *args, **kwargs):
    trenerzy = get_table('trenerzy')
    typy = get_table('typy_dyscyplin')
    group_context = {
        'trenerzy': trenerzy,
        'typy': typy
    }
    return render(request, 'dodawanie_grupy.html', group_context)

def edit_group_view(request, id, *args, **kwargs):
    trenerzy = get_table('trenerzy')
    typy = get_table('typy_dyscyplin')
    grupy = get_table('grupy', condition="id_grupy =" + str(id) + "")[0]
    trenerzy1=[]
    typy1=[]
    atrener=None
    atyp=None
    for t in trenerzy:
        if(t[0]==grupy[2]):
            atrener=(t[0], t[1], t[2])
        else:
            trenerzy1.append(t)
    for t in typy:
        if(t[0]==grupy[3]):
            atyp=t[0]
        else:
            typy1.append(t)
    group_context = {
        'trenerzy': trenerzy1,
        'typy': typy1,
        'grupy': grupy,
        'id': id,
        'atrener': atrener,
        'atyp': atyp
    }
    return render(request, 'edytowanie_grupy.html', group_context)


def competitor_view(request, *args, **kwargs):
    zawodnicy = get_table('zawodnicy')
    if request.method == 'GET':
        [id, nazwisko] = fetch_request_arguments(request, ['id', 'nazwisko'])
        res = search_coach_competitor(nazwisko, id, zawodnicy)
        print(res)
        if res:
            zawodnicy = res

    competitor_context = {
        "zawodnicy": zawodnicy
    }
    return render(request, 'zawodnicy.html', competitor_context)


def detail_competitor_view(request, id, *args, **kwargs):
    zawodnicy = get_table('zawodnicy', condition="id_zawodnika ="+str(id)+"")
    zawodnicy=zawodnicy[0]
    dysc=get_table('uprawiaja', condition="zawodnik ="+str(id)+"")
    grupy=get_table('grupy', condition="id_grupy ="+str(zawodnicy[6])+"")[0]
    grupa=grupy[1]
    data_ur='a'
    if (zawodnicy[4] is not None):
        data = str(zawodnicy[4])
        data_ur = data.split(' ')[0]
        rok = data_ur.split('-')[0]
        miesiac = data_ur.split('-')[1]
        dzien = data_ur.split('-')[2]
        if (dzien[0] == '0'): dzien = dzien[1]
        mie = fetch_month(miesiac)

        data_ur = str(dzien) + ' ' + str(mie) + ' ' + str(rok)
    l = len(dysc)
    detailcompetitor_context = {
        'dysc': dysc,
        'zawodnicy': zawodnicy,
        'data': data_ur,
        'l': l,
        'grupa': grupa,
        'id': id
    }
    return render(request, 'zawodnicy_szczegolowe.html', detailcompetitor_context)


def add_competitor_view(request, *args, **kwargs):
    grupy = get_table('grupy')
    if request.method == 'GET':
        [imie, nazwisko, pesel, data, plec, grupa] = fetch_request_arguments(request,
                                                                             ['imie', 'nazwisko', 'pesel', 'data_ur',
                                                                              'plec', 'grupa'])
        if None not in [imie, nazwisko]:
            kursor = get_cursor()

            if grupa:
                grupa = float(grupa)
            if data:
                data = datetime.strptime(data, '%Y-%m-%d')
            try:
                kursor.callproc('DodajZawodnika', [imie, nazwisko, pesel, data, plec, grupa])
                print('Dodano zawodnika')
            except:
                print('Nie udalo się dodać zawodnika')
            kursor.close()

    add_context = {
        'grupy': grupy
    }
    return render(request, 'dodawanie_zawodnicy.html', add_context)

def edit_competitor_view(request, id, *args, **kwargs):
    grupy=get_table('grupy')
    zawodnicy = get_table('zawodnicy', condition="id_zawodnika ="+str(id)+"")[0]
    edit_context = {
        'grupy': grupy,
        'zawodnicy': zawodnicy,
        'id': id
    }
    return render(request, 'edytowanie_zawodnicy.html', edit_context)

def add_disccomp_view(request, id, *args, **kwargs):
    dysc=get_table('dyscypliny')
    add_context = {
        'dysc': dysc,
        'id': id
    }
    return render(request, 'przypisz_dysc_zaw.html', add_context)

def add_coach_view(request, *args, **kwargs):
    if request.method == 'GET':
        [imie, nazwisko, pesel, data, plec] = fetch_request_arguments(request,['imie', 'nazwisko', 'pesel', 'data_ur', 'plec'])
        if data:
            data = datetime.strptime(data, '%Y-%m-%d')
            kursor = get_cursor()
            try:
                kursor.callproc('DodajTrenera', [imie, nazwisko, pesel, data, plec])
                print('Trener pomyślnie dodany')
            except:
                print('Nie udało się dodać trenera')
            kursor.close()

    return render(request, 'dodawanie_trenerzy.html')


def coach_view(request, *args, **kwargs):
    trenerzy = get_table('trenerzy')

    if request.method == 'GET':
        [id, nazwisko] = fetch_request_arguments(request, ['id', 'nazwisko'])
        res = search_coach_competitor(nazwisko, id, trenerzy)
        if res:
            trenerzy = res
        print(res)
    coach_context = {
        "trenerzy": trenerzy
    }
    return render(request, 'trenerzy.html', coach_context)


def detail_coach_view(request, id, *args, **kwargs):
    trenerzy = get_table('trenerzy', condition="id_trenera =" + str(id) + "")
    trenerzy = trenerzy[0]
    dysc = get_table('szkola', condition="trener =" + str(id) + "")
    data_ur = 'a'
    if (trenerzy[4] is not None):
        data = str(trenerzy[4])
        data_ur = data.split(' ')[0]
        rok = data_ur.split('-')[0]
        miesiac = data_ur.split('-')[1]
        dzien = data_ur.split('-')[2]
        if (dzien[0] == '0'): dzien = dzien[1]
        mie = fetch_month(miesiac)
        data_ur = str(dzien) + ' ' + str(mie) + ' ' + str(rok)
    l = len(dysc)
    detailcoach_context = {
        'dysc': dysc,
        'trenerzy': trenerzy,
        'data': data_ur,
        'l': l,
        'id': id
    }
    return render(request, 'trenerzy_szczegolowe.html', detailcoach_context)

def add_disccoach_view(request, id, *args, **kwargs):
    dysc=get_table('dyscypliny')
    add_context = {
        'dysc': dysc,
        'id': id
    }
    return render(request, 'przypisz_dysc_tren.html', add_context)

def edit_coach_view(request, id, *args, **kwargs):
    trenerzy = get_table('trenerzy', condition="id_trenera ="+str(id)+"")[0]
    edit_context = {
        'trenerzy': trenerzy,
        'id': id
    }
    return render(request, 'edytowanie_trenerzy.html', edit_context)

def plan_view(request, *args, **kwargs):
    plany = get_table('plany_treningowe')
    usrnm = User.get_username(request.user)
    name = usrnm.split('_')[0][1:]
    autorzy = get_table("trenerzy", condition=" imie in ('" + name + "')")
    moje_plany = [a for a in plany if a[1] == autorzy[0][0]]
    plany1 = []
    mplany = []
    for p in plany:
        autor = get_table("trenerzy", condition=" id_trenera =" + str(p[1]) + "")
        a = str(autor[0][1]) + ' ' + str(autor[0][2])
        plany1.append((p[0], a, p[2]))
    for mp in moje_plany:
        autor = get_table("trenerzy", condition=" id_trenera =" + str(p[1]) + "")
        a = str(autor[0][1]) + ' ' + str(autor[0][2])
        mplany.append((mp[0], a, mp[2]))
    l = len(mplany)
    plany_context = {
        "moje_plany": mplany,
        "plany": plany1,
        "l": l
    }

    return render(request, 'plany.html', plany_context)


def detail_plan_view(request, id, *args, **kwargs):
    plan = get_table('plany_treningowe', condition="id_planu =" + str(id) + "")[0]
    trenerzy=get_table('trenerzy', condition="id_trenera =" + str(plan[1]) + "")[0]
    usrnm = User.get_username(request.user)
    name = usrnm.split('_')[0][1:]
    mp=0
    if(name==trenerzy[1]):
        mp=1
    autor=trenerzy[1]+' '+trenerzy[2]
    plan_context = {
        'plan': plan,
        'autor': autor,
        'mp': mp,
        'id': id
    }
    return render(request, 'plan_szczegolowe.html', plan_context)


def add_plan_view(request, *args, **kwargs):
    trenerzy = get_table('trenerzy')
    group_context = {
        'trenerzy': trenerzy,
    }
    return render(request, 'dodawanie_plany.html', group_context)

def edit_plan_view(request, id, *args, **kwargs):
    plany = get_table('plany_treningowe', condition="id_planu =" + str(id) + "")[0]
    trenerzy = get_table('trenerzy')
    trenerzy1=[]
    atrener=None
    for t in trenerzy:
        if(t[0]==plany[1]):
            atrener=(t[0], t[1], t[2])
        else:
            trenerzy1.append(t)
    group_context = {
        'plany': plany,
        'trenerzy': trenerzy1,
        'id': id,
        'autor': atrener
    }
    return render(request, 'edytowanie_plany.html', group_context)

def diet_view(request, *args, **kwargs):
    diety = get_table('diety')
    fnd = True
    if request.method == 'GET':
        [od, do] = fetch_request_arguments(request, ['od', 'do'])
        res = search_diet(od, do, diety)
        if res:
            diety = res
        else:
            diety = []

    diet_context = {
        "diety": diety,
    }
    return render(request, 'diety.html', diet_context)


def add_diet_view(request, *args, **kwargs):
    if request.method == 'GET':
        arg = fetch_request_arguments(request, ['kalorycznosc', 'opis'])
        print(type(arg[1]))
        if not None in arg:
            kursor = get_cursor()
            try:
                kursor.callproc('DodajDiete', [float(arg[0]), arg[1]])
                print('Dodano diete')
            except:
                print('Blad dodania diety')
            kursor.close()
        return render(request, 'dodawanie_diety.html')
    return render(request, 'dodawanie_diety.html')


def discipline_view(request, *args, **kwargs):
    dyscypliny = get_table('dyscypliny')
    discipline_context = {
        "dyscypliny": dyscypliny
    }
    return render(request, 'dyscypliny.html', discipline_context)


def add_disc_view(request, *args, **kwargs):
    typy = [a for a in get_table('typy_dyscyplin')]
    print(typy)

    if request.method == 'GET':
        [nazwa, typ] = fetch_request_arguments(request, ['nazwa', 'typ'])
        print(nazwa, typ)
        if nazwa is not None:
            kursor = get_cursor()
            try:
                kursor.callproc('DodajDyscypline', [nazwa, typ])
            except:
                print('Blad dodawania dyscypliny')
            kursor.close()

    discipline_context = {
        "typy": typy
    }
    return render(request, 'dodawanie_dyscypliny.html', discipline_context)


def typedisc_view(request, *args, **kwargs):
    typy = get_table('typy_dyscyplin')
    typedisc_context = {
        "typy": typy
    }
    return render(request, 'typy.html', typedisc_context)


def add_typedisc_view(request, *args, **kwargs):
    if request.method == 'GET':
        [nazwa] = fetch_request_arguments(request, ['nazwa'])
        if nazwa is not None:
            kursor = get_cursor()
            try:
                kursor.execute("insert into typy_dyscyplin values('{a}')".format(a= nazwa))
                print("Dodano pomyślnie typ dyscypliny")
            except:
                print('Blad dodawania dyscypliny')
            kursor.close()
    return render(request, 'dodawanie_typy.html')


def profile_view(request, *args, **kwargs):
    usrnm = User.get_username(request.user)
    function = usrnm[0]
    if (function == 'T'):
        tabela = get_table('trenerzy')
        funkcja = 'Profil trenera'
    elif (function == 'Z'):
        tabela = get_table('zawodnicy')
        funkcja = 'Profil zawodnika'
    imie = tabela[0][1]
    nazwisko = tabela[0][2]
    if (tabela[0][3] is not None):
        pesel = tabela[0][3]
    else:
        pesel = 'brak danych'
    if (tabela[0][4] is None):
        data_ur = 'brak danych'
    else:
        data_ur = tabela[0][4]
        data_ur = str(data_ur)
        data_ur = data_ur.split(' ')[0]
        rok = data_ur.split('-')[0]
        miesiac = data_ur.split('-')[1]
        dzien = data_ur.split('-')[2]
        if (dzien[0] == '0'): dzien = dzien[1]
        mie = fetch_month(miesiac)

        data_ur = str(dzien) + ' ' + str(mie) + ' ' + str(rok)
    if (tabela[0][5] == 'K'):
        plec = 'Kobieta'
    else:
        plec = 'Mężczyzna'

    profile_context = {
        "imie": imie,
        "nazwisko": nazwisko,
        "pesel": pesel,
        "data_ur": data_ur,
        "funkcja": funkcja,
        "plec": plec
    }
    return render(request, 'profil.html', profile_context)


def usuwanie(request, id, typ, *args, **kwargs):
    cont = {
        "typ": typ
    }
    kursor = get_cursor()

    if typ == 'dieta':
        id = int(id)
        try:
            kursor.execute('delete from diety where id_diety = ' + str(id))
            print('pomyslnie usunieta dieta o id ', id)
            return render(request, 'usuniete.html', cont)

        except:
            print('Blad usuwanie')

    elif typ == 'zawodnik':
        id = int(id)
        try:
            kursor.callproc("UsunZawodnika", [id])
            kursor.close()
            print('Pomyslnie usuniety zaowdnik')
            return render(request, 'usuniete.html', cont)
        except:
            print('Blad usuwania zawodnika')

    elif typ == 'dyscyplina':
        try:
            kursor.execute("delete from dyscypliny where nazwa = '{a}'".format(a=id))
            kursor.close()
            print('Pomyslnie usunieta dyscyplina')
            return render(request, 'usuniete.html', cont)
        except:
            print('Blad usuwania dyscypliny')
    elif typ == 'typ_dyscypliny':
        try:
            print(id)
            kursor.execute("delete from typy_dyscyplin where nazwa_typu = '{a}'".format(a=id))
            kursor.close()
            print('Pomyslnie usuniety typ dyscypliny')
            return render(request, 'usuniete.html', cont)
        except:
            print('Blad usuwania dyscypliny')
    kursor.close()
    print(typ)
    return render(request, 'usuniete.html', cont)


# Obługa błędów
def ErrorView(request, *args, **kwargs):
    return HttpResponse("Błąd połączenia")


def logout_view(request):
    logout(request)
    return home_view(request, 'home_view')
