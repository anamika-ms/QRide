from django.shortcuts import render,redirect
from . models import registration, bus, route
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

def pass_home(request):
    return render(request, 'pass_home.html')

def stu_home(request):
    return render(request, 'stu_home.html')

def bus_home(request):
    user_id = request.session.get('user_id')
    user = registration.objects.get(id=user_id)
    buses = bus.objects.filter(operator=user)
    return render(request, 'bus_home.html', {'buses': buses})


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
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = registration.objects.get(email=email)
            if check_password(password, user.password):
                # Store session info if needed
                request.session['user_id'] = user.id
                request.session['role'] = user.role
                
                # Redirect based on role
                if user.role == 'Passenger':
                    return redirect('pass_home')
                elif user.role == 'Student':
                    return redirect('stu_home')
                elif user.role == 'Operator':
                    return redirect('bus_home')
            else:
                return render(request, 'login.html', {'error': 'Invalid password'})
        except registration.DoesNotExist:
            return render(request, 'login.html', {'error': 'User does not exist'})
    
    return render(request, 'login.html')



def add_bus(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user_id = request.session['user_id']
    user = registration.objects.get(id=user_id)

    # Allow only bus operators
    if user.role != 'Operator':
        messages.error(request, "Access denied! Only bus operators can add buses.")
        return redirect('index')  # Or home page

    if request.method == 'POST':
        bus_number = request.POST.get('bus_number')
        seat_capacity = request.POST.get('seat_capacity')
        bus_route = request.POST.get('bus_route')

        # Check if bus already exists
        if bus.objects.filter(bus_number=bus_number).exists():
            messages.error(request, "Bus with this number already exists!")
            return redirect('add_bus')

        # Save bus
        bus.objects.create(
            operator=user,
            phone=user.phone,
            bus_number=bus_number,
            seat_capacity=seat_capacity,
            bus_route=bus_route
        )

        messages.success(request, "Bus added successfully!")
        return redirect('bus_home')  # Back to operator dashboard

    return render(request, 'add_bus.html')


def add_route(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user_id = request.session['user_id']
    user = registration.objects.get(id=user_id)

    # Allow only bus operators
    if user.role != 'Operator':
        messages.error(request, "Access denied! Only bus operators can add routes.")
        return redirect('index')

    # Get all buses of this operator
    buses = bus.objects.filter(operator=user)

    if request.method == 'POST':
        start_stop = request.POST.get('start_stop')
        end_stop = request.POST.get('end_stop')
        distance = request.POST.get('distance')
        fare = request.POST.get('fare')
        bus_id = request.POST.get('bus')

        selected_bus = bus.objects.get(id=bus_id)

        # Create route
        route.objects.create(
            operator=user,
            bus=selected_bus,
            start_stop=start_stop,
            end_stop=end_stop,
            distance=distance,
            fare=fare
        )

        messages.success(request, "Route added successfully!")
        return redirect('bus_home')

    return render(request, 'add_route.html', {'buses': buses})

def view_routes(request):
    routes = route.objects.all().order_by('-created_at')  # Latest first
    return render(request, 'view_routes.html', {'routes': routes})