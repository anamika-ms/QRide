from django.shortcuts import render,redirect
from . models import registration
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password

# Create your views here.

def index(request):
    return render(request, 'index.html')

def contact(request):
    return render(request, 'contact.html')

def details(request):
    return render(request, 'details.html')

def listing(request):
    return render(request, 'listing.html')


def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone') 
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

        # Password check
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        # Check if email or phone already exists
        if registration.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('register')

        if registration.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already registered!")
            return redirect('register')

        # Save user
        user = registration(
            name=name,
            email=email,
            phone=phone,
            password=make_password(password),
            role=role
        )
        user.save()

        messages.success(request, "Registration successful! Please login.")
        return redirect('login')  # Redirect to login page

    return render(request, 'registration.html')



def login_view(request):
    if request.method == 'POST':
        print(request.POST)  # Debugging
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = registration.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['user_role'] = user.role
                messages.success(request, 'Login successful!')
                return redirect('index')  # Ensure this URL exists
            else:
                messages.error(request, 'Invalid password')
        except registration.DoesNotExist:
            messages.error(request, 'Email not found')

    return render(request, 'login.html')


