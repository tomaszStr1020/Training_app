from djangoProject.settings import get_table, get_cursor
from datetime import datetime, date

'''Wyciąganie miesiąca z liczby'''
def fetch_month(miesiac):
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
    return mie

def fetch_request_arguments(request, names):
    fetched_args=[]
    for a in names:
        try:
            fetched_args.append(request.GET.get(a))
        except:
            fetched_args.append(None)
    print(len(fetched_args), fetched_args)
    return fetched_args

def search_coach_competitor(tabela,nazwisko=None, id=None):
    selected = []
    if nazwisko and not id:
        selected = [a for a in tabela if a[2] == nazwisko]
    elif id and not nazwisko:
        id = int(id)
        selected = [a for a in tabela if a[0] == id]
    elif id and nazwisko:
        id = int(id)
        selected = [a for a in tabela if a[2] == nazwisko and a[0] == id]
    else:
        return False
    return selected

def search_diet(od, do, tabela):
    if od and not do:
        selected = [a for a in tabela if a[1]>=int(od)]
    elif do and not od:
        selected = [a for a in tabela if a[1]<=int(do)]
    elif do and od:
        selected = [a for a in tabela if a[1]>=int(od) and a[1] <=int(do)]
    else:
        return tabela
    return selected

def last_added_competitor():
    kursor = get_cursor()
    try:
        res = [a[0] for a in kursor.execute("select * from zawodnicy where id_zawodnika = (select max(id_zawodnika) from zawodnicy)")]
        kursor.close()
        return res[0]
    except:
        kursor.close()
        return False

def last_added_coach():
    kursor = get_cursor()
    try:
        res = [a[0] for a in kursor.execute("select * from trenerzy where id_trenera = (select max(id_trenera) from trenerzy)")]
        print(res)
        kursor.close()
        return res[0]
    except:
        kursor.close()
        return False

def select_trainings_in_dateframes(od, do, treningi):

    if od and not do:
        od = datetime.strptime(od, '%Y-%m-%d')
        return [a for a in treningi if a[0] >= od]
    elif do and not od:
        do = datetime.strptime(do, '%Y-%m-%d')
        return [a for a in treningi if a[0] <= do]
    elif od and do:
        do = datetime.strptime(do, '%Y-%m-%d')
        od = datetime.strptime(od, '%Y-%m-%d')
        return [a for a in treningi if a[0] <= do and a[0] >= od]
    else:
        return treningi

def czy_rekord(newrecord, nazwa):
    kursor = get_cursor()
    if(newrecord[-1]=='m'):
        newrecord=newrecord[0:-1]
        record=get_table('dyscypliny', condition=" nazwa in ('" + nazwa + "')")[0]
        if(record[1] is not None):
            record=float(record[1])
        else:
            kursor.callproc('PrzypiszRekordKlubu', [newrecord, nazwa])
            kursor.close()
            return 'NOWY REKORD KLUBU!'
        if(float(newrecord)>record):
            kursor.callproc('PrzypiszRekordKlubu', [newrecord, nazwa])
            kursor.close()
            return 'NOWY REKORD KLUBU!'
        elif(float(newrecord)==record):
            kursor.close()
            return 'Wstawiono nowy rekord życiowy! Wyrównano rekord klubu!'
        else:
            kursor.close()
            return 'Wstawiono nowy rekord życiowy!'
    else:
        newrecord1=newrecord.split(':')
        record=get_table('dyscypliny', condition=" nazwa in ('" + nazwa + "')")[0][1]
        if(record is None):
            kursor.callproc('PrzypiszRekordKlubu', [newrecord, nazwa])
            kursor.close()
            return 'NOWY REKORD KLUBU!'
        else:
            record=record.split(':')
        if(len(record)>len(newrecord1)):
            if(len(record)-len(newrecord1)<=1):
                kursor.callproc('PrzypiszRekordKlubu', [newrecord, nazwa])
                kursor.close()
                return 'NOWY REKORD KLUBU!'
            else:
                kursor.close()
                return 'Wstawiono nowy rekord życiowy!'
        elif(len(record)<len(newrecord1)):
            kursor.close()
            return 'Wstawiono nowy rekord życiowy!'
        else:
            for i in range(len(record)):
                if(float(record[i])>float(newrecord1[i])):
                    kursor.callproc('PrzypiszRekordKlubu', [newrecord, nazwa])
                    kursor.close()
                    return 'NOWY REKORD KLUBU!'
                elif(float(record[i])<float(newrecord1[i])):
                    kursor.close()
                    return 'Wstawiono nowy rekord życiowy!'
            kursor.close()
            return 'Wstawiono nowy rekord życiowy! Wyrównano rekord klubu!'