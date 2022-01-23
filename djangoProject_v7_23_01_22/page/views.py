from django.shortcuts import render
from django.http import HttpResponse
from djangoProject.settings import get_table, get_cursor
from django.contrib.auth import logout, get_user
from django.contrib.auth.models import User
from django_datatables_view import *
from django.views import generic
from page.view_functions import *
from datetime import datetime
import string
import random  # define the random module
from account.sender import *
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

    grupy = get_table('grupy')
    usrnm = request.user.get_username().split('_')

    if usrnm[0][0] not in ['Z', 'T']:
        return render(request, 'grupy.html', {'grupy': grupy})

    moje_grupy = [a for a in grupy if a[2] == int(usrnm[0][1:])]
    group_context = {
        "moje_grupy": moje_grupy,
        "grupy": grupy,
    }

    return render(request, 'grupy.html', group_context)


def detail_group_view(request, id, *args, **kwargs):
    grupy = get_table('grupy', condition="id_grupy =" + str(id) + "")
    grupy=grupy[0]
    usrnm = User.get_username(request.user)
    name = usrnm.split('_')[0][1:]
    zawodnicy = get_table('zawodnicy')
    zawod = [a[1:3] for a in zawodnicy if a[6] == int(id)]
    trenerzy=get_table('trenerzy', condition="id_trenera =" + str(grupy[2]) + "")
    mg=0
    if(int(name)==trenerzy[0][0]):
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
    if request.method == 'GET':
        [nazwa, trener, typ] = fetch_request_arguments(request, ['nazwa', 'trener', 'typ'])
        print(trener)
        kursor = get_cursor()
        try:
            kursor.callproc('DodajGrupe', [nazwa, int(trener), typ])
            print('Pomyślnie dodano grupę')
            return group_view(request)
        except:
            print('Nie udało się dodać grupy')
        kursor.close()
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
    if request.method == 'GET':
        [nazwa, trener, typ] = fetch_request_arguments(request, ['nazwa', 'trener', 'typ'])
        kursor = get_cursor()
        try:
            kursor.callproc('EdytujGrupe', [int(id), nazwa, int(trener), typ] )
            print('Pomyślnie zmieniono dane grupy')
            return detail_group_view(request, id)
        except:
            print('Nie udało się edytować danych grupy')
        kursor.close()
    group_context = {
        'trenerzy': trenerzy1,
        'typy': typy1,
        'grupy': grupy,
        'id': id,
        'atrener': atrener,
        'atyp': atyp
    }
    return render(request, 'edytowanie_grupy.html', group_context)

def traininggroup_view(request, id, *args, **kwargs):
    treningi=get_table('treningi', condition="grupa =" + str(id) + "")
    treningi1=[]
    daty=[]
    for t in treningi:
        data = str(t[0])
        data1=data.split(' ')[0]
        print(data1)
        data = data.split(' ')[0]
        rok = data.split('-')[0]
        miesiac = data.split('-')[1]
        dzien = data.split('-')[2]
        if (dzien[0] == '0'): dzien = dzien[1]
        mie = fetch_month(miesiac)
        data = str(dzien) + ' ' + str(mie) + ' ' + str(rok)
        treningi1.append((data, data1))
    trengroup_context = {
        'id': id,
        'treningi': treningi
    }
    return render(request, 'treninggrupy.html', trengroup_context)

def plantraining_view(request, id, *args, **kwargs):
    plany=get_table('plany_treningowe');
    plan_context = {
        'id': id,
        'plany': plany
    }
    return render(request, 'zaplanujtrening.html', plan_context)

def detailtraining_view(request, id, data, *args, **kwargs):
    print(data, type(data))
    treningi=get_table('treningi', condition="grupa ="+str(id)+" and data =TO_DATE('"+data+"','YYYY-MM-DD')")[0]
    plan=get_table('plany_treningowe', condition="id_planu =" + str(treningi[2]) + "")[0]
    opis=plan[2]
    plan_context = {
        'id': id,
        'opis': opis
    }
    return render(request, 'detaletreningu.html', plan_context)

def competitor_view(request, *args, **kwargs):
    zawodnicy = get_table('zawodnicy')
    if request.method == 'GET':
        [id, nazwisko] = fetch_request_arguments(request, ['id', 'nazwisko'])
        res = search_coach_competitor(zawodnicy,nazwisko, id)
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
        [imie, nazwisko, pesel, data, plec, grupa, email] = fetch_request_arguments(request, ['imie', 'nazwisko', 'pesel', 'data_ur', 'plec', 'grupa', 'email'])
        if None not in [imie, nazwisko]:
            kursor = get_cursor()

            if grupa:
                grupa = float(grupa)
            if data:
                data = datetime.strptime(data, '%Y-%m-%d')
            try:
                kursor.callproc('DodajZawodnika', [imie, nazwisko, pesel, data, plec, grupa])
                id = last_added_competitor()
                print(id)
                if id:
                    new_user = "Z"+str(id)+"_"+imie+"_"+nazwisko
                    #Generowanie losowego hasła przy dodawaniu zawodnika
                    S = 10
                    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
                    a = User.objects.create_user(new_user, email, ran, is_staff=False)
                    a.save()
                    email_send("Hasło do konta", "Witaj!\n Oto twoje dane logowania:\nNazwa użytkownika: "+new_user+"\nHasło: "+ran, email)

                    print('Dodano zawodnika i użytkownika z nim powiązanego: '+new_user+' o haśle: '+ran)
                else:
                    print('Dodano tylko do części informacyjnej')
            except:
                print('Nie udalo się dodać zawodnika')
            kursor.close()

    add_context = {
        'grupy': grupy
    }
    return render(request, 'dodawanie_zawodnicy.html', add_context)

def diet_competitor_view(request, id, *args, **kwargs):
    dieta=[(None, None, None)]
    flag=0
    alldiety = get_table('diety')
    zywienie = get_table('zywienie', condition=" zawodnik =" + str(id) + "")
    lenz=len(zywienie)
    print(zywienie)
    if (lenz>0):
        flag=1
        zywienie=zywienie[0]
        diety=get_table('diety', condition=" id_diety in (" + str(zywienie[1]) + ")")[0]
        datazyw=zywienie[2]
        datazyw = str(datazyw)
        datazyw = datazyw.split(' ')[0]
        rok = datazyw.split('-')[0]
        miesiac = datazyw.split('-')[1]
        dzien = datazyw.split('-')[2]
        if (dzien[0] == '0'): dzien = dzien[1]
        mie = fetch_month(miesiac)
        datazyw = str(dzien) + ' ' + str(mie) + ' ' + str(rok)
        dieta = [(diety[1], diety[2], datazyw)]
        print('dieta dla zawodnika',dieta)
    if request.method=='GET':
        diet = fetch_request_arguments(request, [ 'data_diety', 'id_diety'])
        if not None in diet:
            kursor = get_cursor()
            try:
                data = datetime.strptime(diet[0], '%Y-%m-%d')
                print(data, type(diet[1]))
                kursor.callproc('ZaplanujZywienie', [int(id),int(diet[1]), data])
                print('Pomyślnie przypisano dietę')
                return detail_competitor_view(request, id)
            except:
                print('Nie udało się przypisać diety')
            kursor.close()
        else:
            print('Te wartości nie mogą być puste')
    print('flaga:', flag)
    diet_context = {
        "diety": dieta[0],
        "flag": flag,
        "id": id,
        "alldiety": alldiety
    }
    return render(request, 'ustaleniediety.html', diet_context)

def edit_competitor_view(request, id, *args, **kwargs):
    grupy=get_table('grupy')
    zawodnicy = get_table('zawodnicy', condition="id_zawodnika ="+str(id)+"")[0]
    if request.method == 'GET':
        [imie, nazwisko, pesel, data_ur, plec, grupa] = fetch_request_arguments(request, ['imie', 'nazwisko', 'pesel', 'data_ur', 'plec', 'grupa'])
        kursor = get_cursor()
        try:
            data = datetime.strptime(data_ur, '%Y-%m-%d')
            kursor.callproc('EdytujZawodnika', [int(id), imie, nazwisko, pesel, data, plec[0], int(grupa)] )
            print('Pomyślnie zmieniono dane')
            return detail_competitor_view(request, id)
        except:
            print('Nie udało się edytować danych')
        kursor.close()

    edit_context = {
        'grupy': grupy,
        'zawodnicy': zawodnicy,
        'id': id
    }
    return render(request, 'edytowanie_zawodnicy.html', edit_context)

def add_disccomp_view(request, id, *args, **kwargs):
    dysc_all=get_table('dyscypliny')
    print('przypisz dysc: ',id)
    if request.method == 'GET':
        [dysc] = fetch_request_arguments(request, ['dysc'])
        kursor = get_cursor()
        try:
            data = datetime.strptime('2022-01-23', '%Y-%m-%d')
            print(data)
            kursor.callproc('PrzypiszDyscyplineZawodnikowi', [int(id), dysc, data])
            print('Pomyślnie przypisano dyscyplinę zawodnikowi')

        except:
            print('Nie udało się przypisać dyscypliny zawodnikowi')

        kursor.close()

    add_context = {
        'dysc': dysc_all,
        'id': id
    }
    return render(request, 'przypisz_dysc_zaw.html', add_context)

def add_coach_view(request, *args, **kwargs):
    if request.method == 'GET':
        [imie, nazwisko, pesel, data, plec, email] = fetch_request_arguments(request,['imie', 'nazwisko', 'pesel', 'data_ur', 'plec', 'email'])
        if data:
            data = datetime.strptime(data, '%Y-%m-%d')
            kursor = get_cursor()
            try:
                kursor.callproc('DodajTrenera', [imie, nazwisko, pesel, data, plec])
                id = last_added_coach()
                print(id)
                if id:
                    new_user = "T" + str(id) + "_" + imie + "_" + nazwisko
                    # Generowanie losowego hasła przy dodawaniu trenera
                    S = 10
                    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
                    a = User.objects.create_user(new_user, email, ran, is_staff=True)
                    a.save()
                    email_send("Hasło do konta",
                               "Witaj!\n Oto twoje dane logowania:\nNazwa użytkownika: " + new_user + "\nHasło: " + ran, email)

                    print('Dodano trenera i użytkownika z nim powiązanego: ' + new_user + ' o haśle: ' + ran)
                    return coach_view(request)
            except:
                print('Nie udało się dodać trenera')
            kursor.close()

    return render(request, 'dodawanie_trenerzy.html')


def coach_view(request, *args, **kwargs):
    trenerzy = get_table('trenerzy')

    if request.method == 'GET':
        [id, nazwisko] = fetch_request_arguments(request, ['id', 'nazwisko'])
        res = search_coach_competitor(trenerzy,nazwisko, id)
        if res:
            trenerzy = res
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
    dysc_all=get_table('dyscypliny')
    if request.method == 'GET':
        [dysc] = fetch_request_arguments(request, ['dysc'])
        kursor = get_cursor()
        try:
            data = datetime.strptime('2022-01-23', '%Y-%m-%d')
            print(data)
            kursor.callproc('PrzypiszDyscyplineTrenerowi', [int(id), dysc, data])
            print('Pomyślnie przypisano dyscyplinę trenerowi')

        except:
            print('Nie udało się przypisać dyscypliny trenerowi')

        kursor.close()
    add_context = {
        'dysc': dysc_all,
        'id': id
    }
    return render(request, 'przypisz_dysc_tren.html', add_context)

def edit_coach_view(request, id, *args, **kwargs):
    trenerzy = get_table('trenerzy', condition="id_trenera ="+str(id)+"")[0]

    if request.method == 'GET':
        [imie, nazwisko, pesel, data_ur, plec] = fetch_request_arguments(request, ['imie', 'nazwisko', 'pesel', 'data_ur', 'plec'])
        kursor = get_cursor()
        try:
            data = datetime.strptime(data_ur, '%Y-%m-%d')
            kursor.callproc('EdytujTrenera', [int(id), imie, nazwisko, pesel, data, plec[0]] )
            print('Pomyślnie zmieniono dane')
            return detail_coach_view(request, id)
        except:

            print('Nie udało się edytować danych trenera')
        kursor.close()
    edit_context = {
        'trenerzy': trenerzy,
        'id': id
    }
    return render(request, 'edytowanie_trenerzy.html', edit_context)

def plan_view(request, *args, **kwargs):
    plany = get_table('plany_treningowe')
    usrnm = request.user.get_username().split('_')


    moje_plany = [a for a in plany if a[1] == int(usrnm[0][1:])]
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
    if(int(name)==trenerzy[0]):
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

    if request.method == 'GET':
        usr = request.user.get_username()
        print(usr)
        [autor, opis] = fetch_request_arguments(request, ['autor', 'opis'])
        if opis:

            kursor = get_cursor()

            try:
                kursor.callproc('DodajPlan', [int(autor), opis])
                print('Plan opmyslnie dodany dla: ', autor)
                return plan_view(request)
            except:
                print('Nie udało się dodać planu!')
            kursor.close()



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
    name = usrnm.split('_')[0][1:]
    prof=0
    if (function == 'T'):
        tabela = get_table('trenerzy', condition="id_trenera =" + str(name) + "")
        funkcja = 'Profil trenera'
        prof=1
    elif (function == 'Z'):
        tabela = get_table('zawodnicy', condition="id_zawodnika =" + str(name) + "")
        funkcja = 'Profil zawodnika'
        prof=2
    imie = tabela[0][1]
    nazwisko = tabela[0][2]
    grupa=0
    if(prof==2):
        grupa=get_table('grupy', condition="id_grupy =" + str(tabela[0][6]) + "")[0][1]
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
        "plec": plec,
        "prof": prof,
        "grupa": grupa
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
            #Zawodnicy mają is_staff =0, dzięki czemu nawet jeżeli zawodnik i trener mają te same id, nie zajdzie pomyłka
            kursor.callproc("UsunZawodnika", [id])
            kursor.execute("delete from user_auth where id = "+id+ " and is_staff = 0")
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
            kursor.execute("delete from typy_dyscyplin where nazwa_typu = '{a}'".format(a=id))
            kursor.close()
            print('Pomyslnie usuniety typ dyscypliny')
            return render(request, 'usuniete.html', cont)
        except:
            print('Blad usuwania dyscypliny')
    elif typ == 'trener':
        try:
            kursor.callproc('UsunTrenera', [int(id)])
            kursor.close()
            print('Pomyslnie usuniety trener')
            return render(request, 'usuniete.html', cont)
        except:
            print('Blad usuwania dyscypliny')

    kursor.close()
    print(typ)
    return render(request, 'usuniete.html', cont)

def groupzaw_view(request, *args, **kwargs):
    usrnm = User.get_username(request.user)
    name = usrnm.split('_')[0][1:]
    id_g= get_table("zawodnicy", condition=" imie in ('" + name + "')")[0][6]
    grupa=get_table("grupy", condition=" id_grupy in ('" + str(id_g) + "')")[0]
    trener=get_table("trenerzy", condition=" id_trenera in ('" + str(grupa[2]) + "')")[0]
    zawodnicy = get_table('zawodnicy')
    zawod = [a[1:3] for a in zawodnicy if a[6] == grupa[0]]
    group_context = {
        'grupa': grupa,
        'trener': trener,
        'zawod': zawod
    }
    return render(request, 'grupazaw.html', group_context)

def disciplinezaw_view(request, *args, **kwargs):
    dyscyplinyall = get_table('dyscypliny')
    usrnm = User.get_username(request.user)
    name = usrnm.split('_')[0][1:]
    zaw_id=get_table('zawodnicy', condition=" imie in ('" + name + "')")[0][0]
    dyscypliny = get_table('uprawiaja', condition=" zawodnik in ('" + str(zaw_id) + "')")
    dyscypliny1=[]
    for d in dyscypliny:
        rekordklub = get_table('dyscypliny', condition=" nazwa in ('" + d[1] + "')")[0][1]
        dyscypliny1.append((d[1], d[2], d[3], rekordklub ))
    lmd=len(dyscypliny1)
    discipline_context = {
        'dyscypliny': dyscypliny1,
        'lmd': lmd,
        'dyscyplinyall': dyscyplinyall
    }
    return render(request, 'dyscyplinyzaw.html', discipline_context)

def dietzaw_view(request, *args, **kwargs):
    usrnm = User.get_username(request.user)
    name = usrnm.split('_')[0][1:]
    dieta=[(None, None, None)]
    flag=0
    zaw_id = get_table('zawodnicy', condition=" imie in ('" + name + "')")[0][0]
    zywienie = get_table('zywienie', condition=" zawodnik in ('" + str(zaw_id) + "')")
    lenz=len(zywienie)
    if (lenz>0):
        flag=1
        zywienie=zywienie[0]
        diety=get_table('diety', condition=" id_diety in ('" + str(zywienie[1]) + "')")[0]
        datazyw=zywienie[2]
        datazyw = str(datazyw)
        datazyw = datazyw.split(' ')[0]
        rok = datazyw.split('-')[0]
        miesiac = datazyw.split('-')[1]
        dzien = datazyw.split('-')[2]
        if (dzien[0] == '0'): dzien = dzien[1]
        mie = fetch_month(miesiac)
        datazyw = str(dzien) + ' ' + str(mie) + ' ' + str(rok)
        dieta = [(diety[1], diety[2], datazyw)]
    diet_context = {
        "diety": dieta,
        "flag": flag
    }
    return render(request, 'dietyzaw.html', diet_context)

def trainingzaw_view(request, *args, **kwargs):
    return render(request, 'treningizaw.html')

# Obługa błędów
def ErrorView(request, *args, **kwargs):
    return HttpResponse("Błąd połączenia")


def logout_view(request):
    logout(request)
    return home_view(request, 'home_view')
