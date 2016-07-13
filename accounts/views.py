from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.shortcuts import render, redirect
from .forms import UserLoginForm, UserRegisterForm

# Create your views here.


def login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect("/")
    context_data = {
        "form": form,
    }
    print context_data
    return render(request, "blogapp/form.html", context_data)


def register_view(request):
    title = "register"
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        return redirect("/")
    context_data = {
        "form": form,
        'title': title,
    }
    return render(request, "blogapp/form.html", context_data)


def logout_view(request):
    logout(request)
    return redirect("/")
