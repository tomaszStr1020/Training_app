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

def search_coach_competitor(nazwisko, id, tabela):
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








