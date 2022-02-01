from django.shortcuts import render
from django.http import HttpResponse
from djangoProject.settings import get_table, get_cursor
from django.contrib.auth import logout, get_user
from django.contrib.auth.models import User
from django.views import generic
from page.view_functions import *
from datetime import datetime, date
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

    grupy = get_table('grupy', sort="id_grupy")
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
    flag = 0
    trenerzy = get_table('trenerzy')
    typy = get_table('typy_dyscyplin')
    if request.method == 'GET':
        [nazwa, trener, typ] = fetch_request_arguments(request, ['nazwa', 'trener', 'typ'])
        if None not in [nazwa, trener, typ]:
            if '' not in [nazwa, trener, typ]:
                print(trener)
                kursor = get_cursor()
                try:
                    kursor.callproc('DodajGrupe', [nazwa, int(trener), typ])
                    print('Pomyślnie dodano grupę')
                    flag=1
                except:
                    print('Nie udało się dodać grupy')
                    flag=2
                kursor.close()
            else:
                flag=3
    group_context = {
        'trenerzy': trenerzy,
        'typy': typy,
        'flag': flag
    }
    return render(request, 'dodawanie_grupy.html', group_context)

def edit_group_view(request, id, *args, **kwargs):
    flag=0
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
        if None not in [nazwa, trener, typ]:
            if '' not in [nazwa, trener, typ]:
                kursor = get_cursor()
                try:
                    kursor.callproc('EdytujGrupe', [int(id), nazwa, int(trener), typ] )
                    print('Pomyślnie zmieniono dane grupy')
                    return detail_group_view(request, id)
                except:
                    print('Nie udało się edytować danych grupy')
                kursor.close()
            else:
                flag=1
    group_context = {
        'trenerzy': trenerzy1,
        'typy': typy1,
        'grupy': grupy,
        'id': id,
        'atrener': atrener,
        'atyp': atyp,
        'flag': flag
    }
    return render(request, 'edytowanie_grupy.html', group_context)

def traininggroup_view(request, id, *args, **kwargs):
    treningi=get_table('treningi', condition="grupa =" + str(id), sort="data")
    print(treningi)
    treningi1=[]
    if request.method == 'GET':
        [od, do] = fetch_request_arguments(request, ['data_od', 'data_do'])
        treningi = select_trainings_in_dateframes(od, do, treningi)

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
        'treningi': treningi1
    }
    return render(request, 'treninggrupy.html', trengroup_context)

def plantraining_view(request, id, *args, **kwargs):
    plany=get_table('plany_treningowe')
    flag=0
    if request.method == 'GET':
        [id_planu, data_tr] = fetch_request_arguments(request, ['plan', 'data_tr'])
        if None not in [id_planu, data_tr]:
            if '' not in [id_planu, data_tr]:
                kursor = get_cursor()
                try:
                    data = datetime.strptime(data_tr, '%Y-%m-%d')
                    kursor.callproc('ZaplanujTrening', [data, int(id), int(id_planu)])
                    print('Pomyślnie zaplanowany trening')
                    return traininggroup_view(request, id)

                except:
                    print('Nie udało się zaplanować treningu')
                kursor.close()
            else:
                flag=1
    plan_context = {
        'id': id,
        'plany': plany,
        'flag': flag
    }
    return render(request, 'zaplanujtrening.html', plan_context)

def detailtraining_view(request, id, data, *args, **kwargs):
    try:
        treningi=get_table('treningi', condition="grupa ="+str(id)+" and data =TO_DATE('"+data+"','YYYY-MM-DD')")[0]
        print(treningi)
    except:
        return HttpResponse("Błąd wczytywania realizacji")
    plan=get_table('plany_treningowe', condition="id_planu =" + str(treningi[2]) + "")[0]
    opis=plan[2]
    sklad=get_table('zawodnicy', condition="grupa =" + str(id), sort="id_zawodnika")
    realizacja=[]
    for s in sklad:
        real=None
        imienazw=s[1]+" "+s[2]
        real=get_table('realizacje_treningu', condition="zawodnik =" + str(s[0]) + " and grupa ="+str(id)+" and data_treningu =TO_DATE('"+data+"','YYYY-MM-DD')")
        print(real)
        if(len(real)==0):
            r=0
        else:
            r=1
        realizacja.append((s[0], imienazw, r))
    plan_context = {
        'id': id,
        'opis': opis,
        'realizacja': realizacja,
        'data': data
    }
    return render(request, 'detaletreningu.html', plan_context)

def trainingrealization_view(request, id, data, id_zaw, *args, **kwargs):
    real=get_table('realizacje_treningu', condition="zawodnik =" + str(id_zaw) + " and grupa ="+str(id)+" and data_treningu =TO_DATE('"+data+"','YYYY-MM-DD')")[0][1]
    zawodnik=get_table('zawodnicy', condition="id_zawodnika =" + str(id_zaw) + "")[0]
    zaw=zawodnik[1]+" "+zawodnik[2]
    plan_context = {
        'id': id,
        'realizacja': real,
        'zawodnik': zaw,
        'data': data
    }
    return render(request, 'realizacja.html', plan_context)

def competitor_view(request, *args, **kwargs):
    zawodnicy = get_table('zawodnicy', sort="id_zawodnika")
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
    data_ur='brak danych'
    dysc1=[]
    if (zawodnicy[4] is not None):
        data = str(zawodnicy[4])
        data_ur = data.split(' ')[0]
        rok = data_ur.split('-')[0]
        miesiac = data_ur.split('-')[1]
        dzien = data_ur.split('-')[2]
        if (dzien[0] == '0'): dzien = dzien[1]
        mie = fetch_month(miesiac)

        data_ur = str(dzien) + ' ' + str(mie) + ' ' + str(rok)
    for d in dysc:
        data_dysc=None
        if (d[3] is not None):
            data_dysc = str(d[3])
            data_dysc = data_dysc.split(' ')[0]
            rok = data_dysc.split('-')[0]
            miesiac = data_dysc.split('-')[1]
            dzien = data_dysc.split('-')[2]
            if (dzien[0] == '0'): dzien = dzien[1]
            mie = fetch_month(miesiac)

            data_dysc = str(dzien) + ' ' + str(mie) + ' ' + str(rok)
        dysc1.append((d[1],d[2],data_dysc))
    l = len(dysc)
    detailcompetitor_context = {
        'dysc': dysc1,
        'zawodnicy': zawodnicy,
        'data': data_ur,
        'l': l,
        'grupa': grupa,
        'id': id
    }
    return render(request, 'zawodnicy_szczegolowe.html', detailcompetitor_context)

def newrecord_view(request, id, nazwa, *args, **kwargs):
    flag=0
    kom=''
    if request.method == 'GET':
        [rekord] = fetch_request_arguments(request, ['rekord'])
        print(rekord, type(rekord))
        print(nazwa,type(nazwa))
        if None not in [rekord]:
            if '' not in [rekord]:
                kursor = get_cursor()
                kursor.callproc('PrzypiszRekordZyciowy', [rekord, id, nazwa])
                kursor.close()
                kom=czy_rekord(rekord, nazwa)
                flag=2
            else:
                flag=1
    record_context = {
        'id': id,
        'nazwa': nazwa,
        'flag': flag,
        'kom': kom
    }
    return render(request, 'nowyrekord.html', record_context)

def add_competitor_view(request, *args, **kwargs):
    grupy = get_table('grupy')
    flag=0
    if request.method == 'GET':
        [imie, nazwisko, pesel, data, plec, grupa, email] = fetch_request_arguments(request, ['imie', 'nazwisko', 'pesel', 'data_ur', 'plec', 'grupa', 'email'])
        if None not in [imie, nazwisko, email]:
            if '' not in [imie, nazwisko, email]:
                kursor = get_cursor()

                if grupa:
                    grupa = float(grupa)
                if data:
                    data = datetime.strptime(data, '%Y-%m-%d')
                try:
                    kursor.callproc('DodajZawodnika', [imie, nazwisko, pesel, data, plec, grupa])
                    flag=1
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
                    flag=2
                kursor.close()
            else:
                flag=3
    add_context = {
        'grupy': grupy,
        'flag': flag
    }
    return render(request, 'dodawanie_zawodnicy.html', add_context)

def diet_competitor_view(request, id, *args, **kwargs):
    flag = 0
    flag1 = 0
    if request.method=='GET':
        diet = fetch_request_arguments(request, [ 'data_diety', 'id_diety'])
        if not None in diet:
            kursor = get_cursor()
            try:
                data = datetime.strptime(diet[0], '%Y-%m-%d')
                print(data, type(diet[1]))
                kursor.callproc('ZaplanujZywienie', [int(id),int(diet[1]), data])
                print('Pomyślnie przypisano dietę')
                flag1=1
            except:
                print('Nie udało się przypisać diety')
                flag1=2
            kursor.close()
        else:
            print('Te wartości nie mogą być puste')
    dieta=[(None, None, None)]
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
    print('flaga:', flag)
    diet_context = {
        "diety": dieta[0],
        "flag": flag,
        "id": id,
        "alldiety": alldiety,
        "flag1": flag1
    }
    return render(request, 'ustaleniediety.html', diet_context)

def edit_competitor_view(request, id, *args, **kwargs):
    flag=0
    grupy=get_table('grupy')
    zawodnicy = get_table('zawodnicy', condition="id_zawodnika ="+str(id)+"")[0]
    if request.method == 'GET':
        [imie, nazwisko, pesel, data_ur, plec, grupa] = fetch_request_arguments(request, ['imie', 'nazwisko', 'pesel', 'data_ur', 'plec', 'grupa'])
        if '' not in [imie, nazwisko]:
            if grupa is not None:
                kursor = get_cursor()
                try:
                    if data_ur == '':
                        data = zawodnicy[4]
                    else:
                        data = datetime.strptime(data_ur, '%Y-%m-%d')
                    kursor.callproc('EdytujZawodnika', [int(id), imie, nazwisko, pesel, data, plec[0], int(grupa)] )
                    print('Pomyślnie zmieniono dane')
                    return detail_competitor_view(request, id)
                except:
                    print('Nie udało się edytować danych')
                    flag=1
                kursor.close()
        else:
            flag=1
    edit_context = {
        'grupy': grupy,
        'zawodnicy': zawodnicy,
        'id': id,
        'flag': flag
    }
    return render(request, 'edytowanie_zawodnicy.html', edit_context)

def add_disccomp_view(request, id, *args, **kwargs):
    flag=0
    dysc_all=get_table('dyscypliny')
    print('przypisz dysc: ',id)
    if request.method == 'GET':
        [dysc] = fetch_request_arguments(request, ['dysc'])
        if dysc is None:
            flag=0
        else:
            kursor = get_cursor()
            try:
                data = datetime.strptime(str(date.today()), '%Y-%m-%d')
                print(data)
                kursor.callproc('PrzypiszDyscyplineZawodnikowi', [int(id), dysc, data])
                print('Pomyślnie przypisano dyscyplinę zawodnikowi')
                flag=0
                return detail_competitor_view(request, id)

            except:
                print('Nie udało się przypisać dyscypliny zawodnikowi')
                flag=1

            kursor.close()

    add_context = {
        'dysc': dysc_all,
        'id': id,
        'flag': flag
    }
    return render(request, 'przypisz_dysc_zaw.html', add_context)

def add_coach_view(request, *args, **kwargs):
    flag=0
    if request.method == 'GET':
        [imie, nazwisko, pesel, data, plec, email] = fetch_request_arguments(request,['imie', 'nazwisko', 'pesel', 'data_ur', 'plec', 'email'])
        if None not in [imie, nazwisko, email]:
            if '' not in [imie, nazwisko, email]:
                if data:
                    data = datetime.strptime(data, '%Y-%m-%d')
                kursor = get_cursor()
                try:
                    kursor.callproc('DodajTrenera', [imie, nazwisko, pesel, data, plec])
                    flag=1
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
                except:
                    print('Nie udało się dodać trenera')
                    flag=2
                kursor.close()
            else:
                flag=3
    add_context = {
        'flag': flag
    }
    return render(request, 'dodawanie_trenerzy.html', add_context)


def coach_view(request, *args, **kwargs):
    trenerzy = get_table('trenerzy', sort="id_trenera")

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
    dysc1=[]
    if (trenerzy[4] is not None):
        data = str(trenerzy[4])
        data_ur = data.split(' ')[0]
        rok = data_ur.split('-')[0]
        miesiac = data_ur.split('-')[1]
        dzien = data_ur.split('-')[2]
        if (dzien[0] == '0'): dzien = dzien[1]
        mie = fetch_month(miesiac)
        data_ur = str(dzien) + ' ' + str(mie) + ' ' + str(rok)
    for d in dysc:
        data_dysc=None
        if (d[2] is not None):
            data_dysc = str(d[2])
            data_dysc = data_dysc.split(' ')[0]
            rok = data_dysc.split('-')[0]
            miesiac = data_dysc.split('-')[1]
            dzien = data_dysc.split('-')[2]
            if (dzien[0] == '0'): dzien = dzien[1]
            mie = fetch_month(miesiac)

            data_dysc = str(dzien) + ' ' + str(mie) + ' ' + str(rok)
        dysc1.append((d[1],d[2],data_dysc))
    l = len(dysc)
    detailcoach_context = {
        'dysc': dysc1,
        'trenerzy': trenerzy,
        'data': data_ur,
        'l': l,
        'id': id
    }
    return render(request, 'trenerzy_szczegolowe.html', detailcoach_context)

def add_disccoach_view(request, id, *args, **kwargs):
    flag=0
    dysc_all=get_table('dyscypliny')
    if request.method == 'GET':
        [dysc] = fetch_request_arguments(request, ['dysc'])
        if dysc is None:
            flag=0
        else:
            kursor = get_cursor()
            try:
                data = datetime.strptime('2022-01-23', '%Y-%m-%d')
                print(data)
                kursor.callproc('PrzypiszDyscyplineTrenerowi', [int(id), dysc, data])
                print('Pomyślnie przypisano dyscyplinę trenerowi')
                return detail_coach_view(request, id)

            except:
                print('Nie udało się przypisać dyscypliny trenerowi')
                flag=1

            kursor.close()
    add_context = {
        'dysc': dysc_all,
        'id': id,
        'flag': flag
    }
    return render(request, 'przypisz_dysc_tren.html', add_context)

def edit_coach_view(request, id, *args, **kwargs):
    flag=0
    trenerzy = get_table('trenerzy', condition="id_trenera ="+str(id)+"")[0]

    if request.method == 'GET':
        [imie, nazwisko, pesel, data_ur, plec] = fetch_request_arguments(request, ['imie', 'nazwisko', 'pesel', 'data_ur', 'plec'])
        if '' not in [imie, nazwisko]:
            if plec is not None:
                kursor = get_cursor()
                try:
                    if data_ur == '':
                        data = trenerzy[4]
                    else:
                        data = datetime.strptime(data_ur, '%Y-%m-%d')
                    kursor.callproc('EdytujTrenera', [int(id), imie, nazwisko, pesel, data, plec[0]] )
                    print('Pomyślnie zmieniono dane')
                    return detail_coach_view(request, id)
                except:

                    print('Nie udało się edytować danych trenera')
                    flag=1
                kursor.close()
        else: flag=1
    edit_context = {
        'trenerzy': trenerzy,
        'id': id,
        'flag': flag
    }
    return render(request, 'edytowanie_trenerzy.html', edit_context)

def plan_view(request, *args, **kwargs):
    plany = get_table('plany_treningowe', sort="id_planu")
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
    autor=trenerzy[1]+' '+trenerzy[2]
    plan_context = {
        'plan': plan,
        'autor': autor,
        'id': id
    }
    return render(request, 'plan_szczegolowe.html', plan_context)


def add_plan_view(request, *args, **kwargs):
    trenerzy = get_table('trenerzy')
    flag=0
    if request.method == 'GET':
        [autor, opis] = fetch_request_arguments(request, ['autor', 'opis'])
        if None not in [autor, opis]:
            if '' not in [opis]:
                kursor = get_cursor()
                try:
                    kursor.callproc('DodajPlan', [int(autor), opis])
                    print('Plan opmyslnie dodany dla: ', autor)
                    flag=1
                except:
                    print('Nie udało się dodać planu!')
                kursor.close()
            else:
                flag=2

    group_context = {
        'trenerzy': trenerzy,
        'flag': flag
    }
    return render(request, 'dodawanie_plany.html', group_context)

def edit_plan_view(request, id, *args, **kwargs):
    flag=0
    plany = get_table('plany_treningowe', condition="id_planu =" + id)[0]
    trenerzy = get_table('trenerzy')
    if request.method == 'GET':
        [autor, opis] = fetch_request_arguments(request, ['autor', 'opis'])
        if None not in [autor, opis]:
            if '' not in [autor, opis]:
                kursor = get_cursor()
                try:
                    kursor.callproc('EdytujPlan', [int(id), int(autor), opis])
                    print('Pomyślnie edytowano plan')
                    kursor.close()

                    return detail_plan_view(request, id)
                except:
                    print('Nie udało się edytować planu')
            else:
                flag=1
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
        'autor': atrener,
        'flag': flag
    }
    return render(request, 'edytowanie_plany.html', group_context)

def diet_view(request, *args, **kwargs):
    diety = get_table('diety', sort="id_diety")
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
        flag=0
        arg = fetch_request_arguments(request, ['kalorycznosc', 'opis'])
        print(type(arg[1]))
        if None not in arg:
            if arg[0] != '':
                kursor = get_cursor()
                try:
                    kursor.callproc('DodajDiete', [float(arg[0]), arg[1]])
                    print('Dodano diete')
                    flag=1
                except:
                    print('Blad dodania diety')
                kursor.close()
            else:
                flag=2
    add_context={
        'flag': flag
    }
    return render(request, 'dodawanie_diety.html', add_context)


def discipline_view(request, *args, **kwargs):
    dyscypliny = get_table('dyscypliny')
    discipline_context = {
        "dyscypliny": dyscypliny
    }
    return render(request, 'dyscypliny.html', discipline_context)


def add_disc_view(request, *args, **kwargs):
    typy = [a for a in get_table('typy_dyscyplin')]
    print(typy)
    flag=0
    if request.method == 'GET':
        [nazwa, typ] = fetch_request_arguments(request, ['nazwa', 'typ'])
        print(nazwa, typ)
        if None not in [nazwa, typ]:
            if '' not in [nazwa,typ]:
                kursor = get_cursor()
                try:
                    kursor.callproc('DodajDyscypline', [nazwa, typ])
                    flag=1
                except:
                    print('Blad dodawania dyscypliny')
                kursor.close()
            else:
                flag=2
    discipline_context = {
        "typy": typy,
        "flag": flag
    }
    return render(request, 'dodawanie_dyscypliny.html', discipline_context)


def typedisc_view(request, *args, **kwargs):
    typy = get_table('typy_dyscyplin')
    typedisc_context = {
        "typy": typy
    }
    return render(request, 'typy.html', typedisc_context)


def add_typedisc_view(request, *args, **kwargs):
    flag=0
    if request.method == 'GET':
        [nazwa] = fetch_request_arguments(request, ['nazwa'])
        if nazwa is not None:
            if nazwa != '':
                kursor = get_cursor()
                try:
                    kursor.execute("insert into typy_dyscyplin values('{a}')".format(a= nazwa))
                    print("Dodano pomyślnie typ dyscypliny")
                    flag=1
                except:
                    print('Blad dodawania dyscypliny')
                kursor.close()
            else:
                flag=2
    add_context={
        'flag': flag
    }
    return render(request, 'dodawanie_typy.html', add_context)


def profile_view(request, *args, **kwargs):
    usrnm = User.get_username(request.user)
    print(usrnm)
    function = usrnm[0]
    name = usrnm.split('_')[0][1:]
    print(name)
    prof=0
    if (function == 'T'):
        tabela = get_table('trenerzy', condition="id_trenera =" + str(name) + "")
        funkcja = 'Profil trenera'
        prof=1
    elif (function == 'Z'):
        tabela = get_table('zawodnicy', condition="id_zawodnika =" + str(name) + "")
        print(tabela)
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
        "grupa": grupa,
        "id": name
    }
    return render(request, 'profil.html', profile_context)


def usuwanie(request, id, typ, *args, **kwargs):
    cont = {
        "typ": typ,
        "error": 0
    }
    kursor = get_cursor()
    error = 0

    if typ == 'dieta':

        try:
            print(id)
            kursor.execute("delete from diety where id_diety =" + id)
            print('pomyslnie usunieta dieta o id ', id)
            kursor.close()
            return render(request, 'usuniete.html', cont)

        except:
            error = 'Dieta jest obecnie wykorzystywana przez zawodnika/ów'
            print('Blad usuwania diety')

    elif typ == 'zawodnik':
        id = int(id)
        try:
            #Zawodnicy mają is_staff =0, dzięki czemu nawet jeżeli zawodnik i trener mają te same id, nie zajdzie pomyłka
            kursor.callproc("UsunZawodnika", [id])
            try:
                kursor.execute("delete from user_auth where id = "+str(id)+ " and is_staff = 0")
            except:
                pass
            kursor.close()
            print('Pomyslnie usuniety zaowdnik')
            return render(request, 'usuniete.html', cont)
        except:
            print('Blad usuwania zawodnika')

    elif typ == 'dyscyplina':
        try:
            kursor.callproc('UsunDyscypline', [id])
            kursor.close()
            print('Pomyslnie usunieta dyscyplina')
            return render(request, 'usuniete.html', cont)
        except:
            error=''
            print('Blad usuwania dyscypliny')
    elif typ == 'typ_dyscypliny':
        try:
            kursor.execute("delete from typy_dyscyplin where nazwa_typu = '{a}'".format(a=id))
            kursor.close()
            print('Pomyslnie usuniety typ dyscypliny')
            return render(request, 'usuniete.html', cont)
        except:
            error='Typ dyscypliny jest przypisany do dyscypliny lub grupy. Zmień typ dyscypliny dla grupy lub dla dyscypliny, abyś mógł go usunąć.'
            print('Blad usuwania dyscypliny')
    elif typ == 'trener':
        try:
            kursor.callproc('UsunTrenera', [int(id)])
            try:
                kursor.execute("delete from user_auth where id = "+str(id)+ " and is_staff = 1")
            except:
                pass
            kursor.close()
            print('Pomyslnie usuniety trener')
            return render(request, 'usuniete.html', cont)
        except:
            error= 'Nie można usunąć trenera, który prowadzi grupę lub jest autorem planu treningowego!\n' \
                   'Zmień trenera grupy, lub przypisz plan innemu trenerowi.'
            print('Blad usuwania trenera')

    elif typ == 'grupa':
        try:
            kursor.callproc('UsunGrupe', [int(id)])
            kursor.close()
            print('Pomyslnie usunieta grupa')
            return render(request, 'usuniete.html', cont)
        except:
            error= 'Nie można usunąć grupy, ponieważ w jej składzie są zawodnicy. Zmień grupę zawodnikom, którzy należą do tej którą chcesz usunąć.'
            print('Blad usuwania grupy')
    else:
        try:
            kursor.callproc("UsunUprawiaja", [int(id), typ])
            kursor.close()
            print('Pomyslnie usunieta uprawiaja')
            return render(request, 'usuniete.html', {'typ': typ, 'id_zaw': id})
        except:
            print('Blad usuwania uprawiaja')

    kursor.close()


    cont = {
        "typ": typ,
        "error": error
    }

    print(typ)
    return render(request, 'usuniete.html', cont)

def usuwanie_szkola(request, id, typ, dyscyplina, *args, **kwargs):
    kursor = get_cursor()

    try:
        kursor.callproc("UsunSzkola", [int(id), dyscyplina])
        print('Pomyslnie usunieta uprawiaja')
        kursor.close()
        return render(request, 'usuniete.html', {'typ': typ, 'id_tren': id, 'error': 0})
    except:
        print('Blad usuwania grupy')
    kursor.close()
    return render(request, 'usuniete.html', {'typ': typ, 'error': 'Nie udało się usunąć szkolonej dyscypliny'})

def groupzaw_view(request, *args, **kwargs):
    usrnm = User.get_username(request.user)
    id = usrnm.split('_')[0][1:]
    id_grupy = get_table("zawodnicy", condition= " id_zawodnika = "+id)[0][6]
    print(id_grupy)
    grupa=get_table("grupy", condition=" id_grupy = " + str(id_grupy))[0]
    trener=get_table("trenerzy", condition=" id_trenera in (" + str(grupa[2]) + ")")[0]
    zawodnicy = get_table('zawodnicy', sort="nazwisko")
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
    name = usrnm.split('_')[1]
    zaw_id=get_table('zawodnicy', condition=" imie in ('" + name + "')")[0][0]
    dyscypliny = get_table('uprawiaja', condition=" zawodnik in ('" + str(zaw_id) + "')")
    dyscypliny1=[]
    for d in dyscypliny:
        rekordklub = get_table('dyscypliny', condition=" nazwa in ('" + d[1] + "')")[0][1]
        if (d[3] is not None):
            data_dysc = str(d[3])
            data_dysc = data_dysc.split(' ')[0]
            rok = data_dysc.split('-')[0]
            miesiac = data_dysc.split('-')[1]
            dzien = data_dysc.split('-')[2]
            if (dzien[0] == '0'): dzien = dzien[1]
            mie = fetch_month(miesiac)

            data_dysc = str(dzien) + ' ' + str(mie) + ' ' + str(rok)

        dyscypliny1.append((d[1], d[2], data_dysc, rekordklub ))
    lmd=len(dyscypliny1)
    discipline_context = {
        'dyscypliny': dyscypliny1,
        'lmd': lmd,
        'dyscyplinyall': dyscyplinyall
    }
    return render(request, 'dyscyplinyzaw.html', discipline_context)

def dietzaw_view(request, *args, **kwargs):
    usrnm = User.get_username(request.user)
    id = usrnm.split('_')[0][1:]
    dieta=[(None, None, None)]
    flag=0
    zywienie = get_table('zywienie', condition=" zawodnik =" + str(id) )
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
        dieta = (diety[1], diety[2], datazyw)
    diet_context = {
        "dieta": dieta,
        "flag": flag
    }
    return render(request, 'dietyzaw.html', diet_context)

def trainingzaw_view(request, *args, **kwargs):
    id_zaw = request.user.get_username().split('_')[0][1:]
    id_grupy = get_table('zawodnicy', condition=' id_zawodnika = '+ id_zaw)[0][6]
    treningi = get_table('treningi', condition=' grupa = '+str(id_grupy), sort="data")
    treningi1=[]
    if request.method == 'GET':
        [od, do] = fetch_request_arguments(request, ['data_od', 'data_do'])
        treningi = select_trainings_in_dateframes(od, do, treningi)
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

    context = {
        'treningi': treningi1,
        'id_zaw': id_zaw,
        'id_grupy': id_grupy
    }

    return render(request, 'treningizaw.html', context)

def trainingrealization_comp_view(request, id, data, *args, **kwargs):
    id_zaw = request.user.get_username().split('_')[0][1:]
    print(id, data, 'W traning')
    id_planu =get_table('treningi', condition="grupa ="+str(id)+" and data =TO_DATE('"+data+"','YYYY-MM-DD')")[0][2]
    plan = get_table('plany_treningowe', condition=' id_planu = '+str(id_planu))[0]
    flag=0
    real=get_table('realizacje_treningu', condition="zawodnik =" + str(id_zaw) + " and grupa ="+str(id)+" and data_treningu =TO_DATE('"+data+"','YYYY-MM-DD')")
    if real:
        real = real[0][1]
        flag=1

    plan_context = {
        'id': id,
        'realizacja': real,
        'plan': plan,
        'data': data,
        'flag': flag

    }
    return render(request, 'dodawanie_realizacji.html', plan_context)

def edit_real_view(request, id,data, *args, **kwargs):
    flaga = 0
    id_zaw = request.user.get_username().split('_')[0][1:]
    real = get_table('realizacje_treningu', condition="zawodnik =" + str(id_zaw) + " and grupa =" + str(
        id) + " and data_treningu =TO_DATE('" + data + "','YYYY-MM-DD')")

    if real:
        # if real[0][1] == None:
        #     group_context = {
        #         'plan': real,
        #         'flaga': flaga,
        #         'id': id,
        #         'data': data
        #     }
        #     return render(request, 'edytowanie_realizacji.html', group_context)
        real = real[0][1]
        flaga = 1
        print(real, flaga)

    if request.method == 'GET':
        print('Weszło do geta')
        [opis] = fetch_request_arguments(request, ['opis'])
        if None not in [opis]:

            kursor = get_cursor()
            try:
                if (flaga==1):

                    kursor.execute("update realizacje_treningu set wykonanie = '{vOpis}' where zawodnik = {vId} and data_treningu = TO_DATE('{vData}', 'YYYY-MM-DD') and grupa = {vGrupa}".format(vOpis = opis, vId =id_zaw, vData=data, vGrupa = id))
                    kursor.close()
                    return trainingrealization_comp_view(request, id, data)
                else:
                    kursor.execute("insert into realizacje_treningu values({vId}, '{vOpis}', TO_DATE('{vData}', 'YYYY-MM-DD'), {vGrupa})".format(vOpis = opis, vId =id_zaw, vData=data, vGrupa = id))
                    kursor.close()
                    return trainingrealization_comp_view(request, id, data)
            except:
                print('Nie udało się edytować realizacji')
                kursor.close()


    group_context = {
        'plan': real,
        'flaga': flaga,
        'id': id,
        'data': data
    }
    return render(request, 'edytowanie_realizacji.html', group_context)


# Obługa błędów
def ErrorView(request, *args, **kwargs):
    return HttpResponse("Błąd połączenia")


def logout_view(request):
    logout(request)
    return home_view(request, 'home_view')
