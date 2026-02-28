from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, ProfileForm, EditProfileForm
from borrowing.models import BorrowRecord


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)  # 2 weeks
            return redirect(request.POST.get('next') or 'home')
        error = 'Invalid username or password. Please try again.'
    return render(request, 'accounts/login.html', {
        'error': error,
        'next': request.GET.get('next', ''),
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to the library.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    borrow_records = BorrowRecord.objects.filter(
        student=request.user
    ).select_related('book').order_by('-borrow_date')

    stats = {
        'currently_borrowed': borrow_records.filter(status='borrowed').count(),
        'total_borrowed': borrow_records.count(),
        'returned': borrow_records.filter(status='returned').count(),
    }

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
        if form.is_valid():
            profile_obj = form.save(commit=False)
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            profile_obj.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile, user=request.user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'borrow_records': borrow_records,
        'stats': stats,
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(
            request.POST, request.FILES,
            instance=request.user.profile,
            user=request.user,
        )
        if form.is_valid():
            profile_obj = form.save(commit=False)
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            new_pw = form.cleaned_data.get('new_password')
            if new_pw:
                request.user.set_password(new_pw)
                update_session_auth_hash(request, request.user)
            request.user.save()
            profile_obj.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user.profile, user=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})
