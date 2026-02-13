from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm
from django.utils import timezone
from django.shortcuts import HttpResponse


def age_verification(request):
    """Simple DOB-based age verification view.

    Sets `request.session['is_age_verified'] = True` when user provides a DOB
    that makes them at least the configured minimum age.
    """
    from datetime import datetime
    from django.conf import settings

    next_url = request.GET.get('next', 'store:home')

    if request.method == 'POST':
        dob = request.POST.get('dob')
        try:
            dob_dt = datetime.strptime(dob, '%Y-%m-%d').date()
            today = timezone.now().date()
            age = (today - dob_dt).days // 365
            min_age = getattr(settings, 'CANNABIS_MIN_AGE', 18)
            if age >= min_age:
                request.session['is_age_verified'] = True
                # Persist to user profile for authenticated users so they only verify once
                if request.user.is_authenticated:
                    try:
                        profile = request.user.userprofile
                        profile.age_verified = True
                        profile.age_verified_at = timezone.now()
                        profile.save()
                    except Exception:
                        pass
                return redirect(next_url)
            else:
                return HttpResponse(f'You must be at least {min_age} years old to purchase regulated cannabis products.')
        except Exception:
            return HttpResponse('Invalid date provided.', status=400)

    context = {'next': next_url}
    return render(request, 'accounts/age_verification.html', context)


def confirm_age(request):
    """Simple endpoint to mark session/user as age-verified when user clicks a confirmation (AJAX or form)."""
    from django.views.decorators.http import require_POST
    from django.http import JsonResponse

    @require_POST
    def _post(req):
        next_url = req.POST.get('next', '/')
        req.session['is_age_verified'] = True
        if req.user.is_authenticated:
            try:
                profile = req.user.userprofile
                profile.age_verified = True
                profile.age_verified_at = timezone.now()
                profile.save()
            except Exception:
                pass
        return JsonResponse({'ok': True, 'next': next_url})

    return _post(request)


def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('store:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('store:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('store:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'store:home')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    context = {'form': form}
    return render(request, 'accounts/login.html', context)


@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('store:home')


@login_required
def profile(request):
    """User profile"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    context = {'form': form}
    return render(request, 'accounts/profile.html', context)
