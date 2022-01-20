from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login


from .forms import LoginForm

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)

                    return render(request, 'login.html', {'form': form})
                else:
                    return HttpResponse("Konto zablokowane")
            else:
                return HttpResponse("Nieprawidłowe dane logowanie")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def redirect_view(request):
    response = redirect('/home')
    return response