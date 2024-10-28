from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .forms import *
from .models import Comment, BlogModel, Profile, OTP
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.utils import timezone


def logout_view(request):
    logout(request)
    return redirect('/')


def home(request):
    context = {
        'blogs': BlogModel.objects.all(),
    }
    return render(request, 'home.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('verify_otp')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def blog_detail(request, slug):
    blog_obj = get_object_or_404(BlogModel, slug=slug)
    comments = Comment.objects.filter(blog=blog_obj)
    context = {
        'blog_obj': blog_obj,
        'comments': comments,
    }
    return render(request, 'blog_detail.html', context)


def add_comment(request, slug):
    if request.method == 'POST':
        text = request.POST.get('text')
        blog = get_object_or_404(BlogModel, slug=slug)
        Comment.objects.create(user=request.user, blog=blog, text=text)
        return redirect('blog_detail', slug=slug)
    return redirect('home')

@login_required
def see_blog(request):
    blog_objs = BlogModel.objects.filter(user=request.user)
    return render(request, 'see_blog.html', {'blog_objs': blog_objs})


@login_required
def add_blog(request):
    context = {'form': BlogForm}
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            title = request.POST.get('title')
            content = form.cleaned_data['content']
            user = request.user
            image = request.FILES.get('image', '')

            BlogModel.objects.create(user=user, title=title, content=content, image=image)
            return redirect('/add-blog/')
    return render(request, 'add_blog.html', context)


@login_required
def blog_update(request, slug):
    blog_obj = get_object_or_404(BlogModel, slug=slug)

    if blog_obj.user != request.user:
        return redirect('/')

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog_obj.title = request.POST.get('title')
            blog_obj.content = form.cleaned_data['content']
            blog_obj.image = request.FILES.get('image', blog_obj.image)
            blog_obj.save()
            return redirect('blog_detail', slug=blog_obj.slug)

    context = {
        'blog_obj': blog_obj,
        'form': BlogForm(initial={'content': blog_obj.content}),
    }
    return render(request, 'update_blog.html', context)


@login_required
def blog_delete(request, id):
    blog_obj = get_object_or_404(BlogModel, id=id)

    if blog_obj.user == request.user:
        blog_obj.delete()

    return redirect('/see-blog/')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            if User.objects.filter(username=username).exists():
                form.add_error('username', 'This username is already taken. Please choose a different one.')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                profile = Profile.objects.create(user=user, is_verified=False)
                profile.save()

                login(request, user)

                otp_instance = OTP.objects.create(user=user)
                otp_code = otp_instance.generate_otp()
                otp_instance.otp_code = otp_code
                otp_instance.save()

                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {otp_code}. It is valid for 5 minutes.',
                    'rravi5604@gmail.com',
                    [email],
                    fail_silently=False,
                )

                messages.success(request, 'Registration successful! Please check your email for the OTP.')
                return redirect('verify_otp')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

def send_otp(request):
    user = request.user
    otp_instance, created = OTP.objects.get_or_create(user=user)
    otp_code = otp_instance.generate_otp()
    otp_instance.otp_code = otp_code
    otp_instance.save()

    try:
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {otp_code}. It is valid for 5 minutes.',
            'rravi5604@gmail.com',
            [user.email],
            fail_silently=False,
        )
    except BadHeaderError:
        print("Invalid header found.")
        messages.error(request, "There was an error sending the email. Please try again.")
    except Exception as e:
        print(f"An error occurred: {e}")
        messages.error(request, "An unexpected error occurred. Please try again.")

    return redirect('verify_otp')


@login_required
def verify_otp(request):
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')

        try:
            otp_instance = OTP.objects.get(user=request.user)

            if otp_instance.otp_code == otp_code:
                try:
                    profile = Profile.objects.get(user=request.user)
                    profile.is_verified = True
                    profile.save()

                    messages.success(request, 'OTP verified successfully! Your account is now active.')
                    return redirect('home')
                except Profile.DoesNotExist:
                    messages.error(request, 'Profile does not exist for this user.')
                    return redirect('login')

            else:
                messages.error(request, 'Invalid OTP. Please try again.')

        except OTP.DoesNotExist:
            messages.error(request, 'OTP not found. Please request a new one.')

    return render(request, 'verify_otp.html')
