from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from shop.forms import LoginForm, UserRegistrationForm


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/')
                return redirect('register')
            else:
                messages.add_message(request, messages.INFO, 'Wrong login or password!')
                return redirect('login')
    form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            cd = user_form.cleaned_data
            new_user = User.objects.create_user(username=cd['username'],
                                                first_name=cd['first_name'],
                                                last_name=cd['last_name'],
                                                email=cd['email'],
                                                password=cd['password'])
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required(login_url='login/')
def logout_user(request):
    logout(request)
    return redirect('login')
