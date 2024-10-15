from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.core.cache import cache
import time

# Registrierung
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Nach der Registrierung zur Startseite weiterleiten
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                # Rate limiting: Check if user is rate limited
                login_attempts = cache.get(f'login_attempts_{user.username}', 0)
                if login_attempts >= 5:
                    return render(request, 'accounts/login.html', {'form': form, 'error': 'Zu viele fehlgeschlagene Login-Versuche. Bitte versuchen Sie es später erneut.'})
                
                login(request, user)
                cache.set(f'login_attempts_{user.username}', 0, timeout=300)  # Reset login attempts on successful login
                return redirect('home')  # Nach dem Login zur Startseite weiterleiten
            else:
                cache.incr(f'login_attempts_{request.POST.get("username")}', 1)
                cache.expire(f'login_attempts_{request.POST.get("username")}', 300)  # Set timeout for 5 minutes
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Logout
def logout_view(request):
    logout(request)
    return render(request, 'accounts/logout.html', {'message': 'Sie haben sich erfolgreich abgemeldet.'})