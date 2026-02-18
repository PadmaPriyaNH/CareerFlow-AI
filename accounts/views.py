from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required

from django.urls import reverse

from .forms import EmailOrUsernameAuthenticationForm

def login_choice(request):
    return render(request, 'accounts/login_choice.html')

def user_login(request):
    form = EmailOrUsernameAuthenticationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if user:
            auth_login(request, user)
            return redirect('dashboard')
    return render(request, 'accounts/user_login.html', {'form': form})

def admin_login(request):
    error = False
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_superuser:
            auth_login(request, user)
            return redirect(reverse('admin:index'))
        else:
            error = True
    return render(request, 'accounts/admin_login.html', {'form': {}, 'error': error})
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import EmailOrUsernameAuthenticationForm, CustomUserCreationForm
def custom_login(request):
    if request.method == 'POST':
        form = EmailOrUsernameAuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                return redirect('dashboard')
    else:
        form = EmailOrUsernameAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile(request):
    """User profile page allowing basic updates"""
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', user.email)
        user.save()

        profile = getattr(user, 'profile', None)
        if profile:
            profile.phone_number = request.POST.get('phone_number', '')
            profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard')

    # Render the profile page for both GET and POST
    profile = getattr(user, 'profile', None)
    return render(request, 'accounts/profile.html', {
        'user': user,
        'profile': profile,
    })

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})
