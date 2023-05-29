from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm

def register(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Создан аккаунт {username}!')
            return redirect('index')
    else:
        form = UserRegisterForm()
    return render(request, 'users/auth.html', {'form': form, 'user':user})

