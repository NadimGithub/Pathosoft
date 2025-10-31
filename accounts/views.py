from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .models import CustomUser
from .forms import CustomUserCreationForm , CustomUserChangeForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# @login_required(login_url='login')
# def dashboard(request):
#     return render(request, 'dashboard.html')

@login_required
def dashboard(request):
    lab = request.user.lab
    # example - show lab specific data
    # labs_tests = Test.objects.filter(lab=lab)
    # labs_patients = Patient.objects.filter(lab=lab)
    return render(request, 'dashboard.html', {'lab': lab})


def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print(form.errors)
        print(form.data)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please login.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']

            # check login by username or email
            user = authenticate(request, username=username_or_email, password=password)
            if user is None:
                try:
                    user_obj = CustomUser.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    user = None

            if user is not None:
                login(request, user)
                return redirect('dashboard')  # after login redirect to dashboard
            else:
                messages.error(request, "Invalid username/email or password.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('login')


def forgot_password(request):
    return render(request, 'accounts/forgot_password.html')

@login_required
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_users')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/create_user.html', {'form': form})

@login_required
def edit_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('view_users')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'accounts/edit_user.html', {'form': form, 'user': user})

@login_required(login_url='login')
def view_users(request):
    query = request.GET.get('q', '').strip()
    users = CustomUser.objects.all().order_by('-id')

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    paginator = Paginator(users, 3)  # 5 users per page
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)

    return render(request, 'accounts/view_users.html', {
        'users': users_page,
        'query': query,
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        
            return redirect('dashboard')
    return render(request, 'accounts/change_password.html')
# ...existing code...