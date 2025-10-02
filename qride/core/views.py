from django.shortcuts import render, redirect, get_object_or_404
from .models import registration, bus, route, ticket,payment
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponse
import random
import string
from django.conf import settings
from io import BytesIO
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
import razorpay


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


# Registration
def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone') 
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if registration.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('register')

        if registration.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already registered!")
            return redirect('register')

        user = registration(
            name=name,
            email=email,
            phone=phone,
            password=make_password(password),
            role=role
        )
        user.save()

        messages.success(request, "Registration successful! Please login.")
        return redirect('login')

    return render(request, 'registration.html')


# Login
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = registration.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['role'] = user.role

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


# Add Bus 
def add_bus(request):
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user_id = request.session['user_id']
    user = registration.objects.get(id=user_id)

    if user.role != 'Operator':
        messages.error(request, "Access denied! Only bus operators can add buses.")
        return redirect('index')

    if request.method == 'POST':
        bus_number = request.POST.get('bus_number')
        seat_capacity = request.POST.get('seat_capacity')
        bus_route = request.POST.get('bus_route')

        if bus.objects.filter(bus_number=bus_number).exists():
            messages.error(request, "Bus with this number already exists!")
            return redirect('add_bus')

        bus.objects.create(
            operator=user,
            phone=user.phone,
            bus_number=bus_number,
            seat_capacity=seat_capacity,
            bus_route=bus_route
        )

        messages.success(request, "Bus added successfully!")
        return redirect('bus_home')

    return render(request, 'add_bus.html')


# Add Route
def add_route(request):
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user_id = request.session['user_id']
    user = registration.objects.get(id=user_id)

    if user.role != 'Operator':
        messages.error(request, "Access denied! Only bus operators can add routes.")
        return redirect('index')

    buses = bus.objects.filter(operator=user)

    if request.method == 'POST':
        start_stop = request.POST.get('start_stop')
        end_stop = request.POST.get('end_stop')
        distance = request.POST.get('distance')
        fare = request.POST.get('fare')
        bus_id = request.POST.get('bus')

        selected_bus = bus.objects.get(id=bus_id)

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


# View Routes
def view_routes(request):
    routes = route.objects.all().order_by('-created_at')
    return render(request, 'view_routes.html', {'routes': routes})


# Select Destination
def select_destination(request):
    bus_id = request.GET.get('bus_id')
    if not bus_id:
        return HttpResponse("Bus ID not provided", status=400)

    bus_obj = get_object_or_404(bus, id=bus_id)
    routes = route.objects.filter(bus=bus_obj)

    return render(request, 'select_destination.html', {
        'bus': bus_obj,
        'routes': routes
    })


# Ticket Generation
def generate_ticket(request, bus_id, route_id):
    # Check if user is logged in
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login first.")
        return redirect('login')

    passenger = get_object_or_404(registration, id=user_id)
    selected_bus = get_object_or_404(bus, id=bus_id)
    selected_route = get_object_or_404(route, id=route_id)
    fare_amount = selected_route.total

    # Generate random ticket number
    ticket_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Create ticket
    new_ticket = ticket.objects.create(
        passenger=passenger,
        bus=selected_bus,
        route=selected_route,
        fare=fare_amount,
        ticket_number=ticket_number
    )

    # Create corresponding pending payment
    payment.objects.create(
        ticket=new_ticket,
        amount=fare_amount,
        status="pending"
    )

    # Store ticket id in session to use for payment
    request.session['current_ticket_id'] = new_ticket.id

    return render(request, 'ticket.html', {'ticket': new_ticket})


# Operator Tickets
def operator_tickets(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login first.")
        return redirect('login')

    user = get_object_or_404(registration, id=user_id)

    if user.role != 'Operator':
        messages.error(request, "Access denied! Only operators can view tickets.")
        return redirect('index')

    operator_buses = bus.objects.filter(operator=user)
    tickets = ticket.objects.filter(bus__in=operator_buses).order_by('-created_at')

    return render(request, 'operator_tickets.html', {'tickets': tickets})


# Travel History
def travel_history(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login first.")
        return redirect('login')

    passenger = get_object_or_404(registration, id=user_id)

    if passenger.role not in ['Passenger', 'Student']:
        messages.error(request, "Access denied! Only passengers or students can view travel history.")
        return redirect('index')

    tickets = ticket.objects.filter(passenger=passenger).order_by('-created_at')
    return render(request, 'travel_history.html', {'tickets': tickets})


def view_ticket(request, ticket_id):
    ticket_obj = get_object_or_404(ticket, id=ticket_id)
    return render(request, 'ticket.html', {'ticket': ticket_obj})



def initiate_payment(request, ticket_id):
    t = get_object_or_404(ticket, id=ticket_id)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount_paise = int(t.fare * 100)  # Razorpay amount in paise

    # Create an order
    razorpay_order = client.order.create({
        'amount': amount_paise,
        'currency': 'INR',
        'payment_capture': '1'
    })

    # --- Debug print ---
    print("Razorpay Order Created:", razorpay_order)
    print("Amount in paise:", amount_paise)
    print("Ticket ID:", t.id)

    # Save order id in payment record
    pay_obj = t.payment
    pay_obj.transaction_id = razorpay_order['id']
    pay_obj.status = 'pending'
    pay_obj.save()

    context = {
        'ticket': t,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount_paise,
        'currency': 'INR'
    }
    return render(request, 'razorpay_payment.html', context)



def payment_success(request, ticket_id):
    t = get_object_or_404(ticket, id=ticket_id)
    payment_id = request.GET.get('payment_id')

    # Update payment record
    pay_obj = t.payment
    pay_obj.transaction_id = payment_id
    pay_obj.status = 'success'
    pay_obj.save()

    return redirect('generate_ticket', bus_id=t.bus.id, route_id=t.route.id)


def download_ticket(request, ticket_id):
    t = get_object_or_404(ticket, id=ticket_id)

    # Create a PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "QRide Bus Ticket")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, 760, f"Ticket Number: {t.ticket_number}")
    p.drawString(50, 740, f"Bus Number: {t.bus.bus_number}")
    p.drawString(50, 720, f"Route: {t.route.start_stop} → {t.route.end_stop}")
    p.drawString(50, 700, f"Passenger: {t.passenger.name}")
    p.drawString(50, 680, f"Fare: {t.fare}/-")
    
    p.showPage()
    p.save()
    buffer.seek(0)

    # Return PDF as response
    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename=ticket_{t.ticket_number}.pdf'
    })


def operator_bus_report(request, bus_id):
    bus_obj = get_object_or_404(bus, id=bus_id)
    tickets = ticket.objects.filter(bus=bus_obj)

    # PDF generation
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(150, y, f"Tickets Report for Bus {bus_obj.bus_number}")
    y -= 40

    total_earned = 0
    p.setFont("Helvetica", 12)

    for t in tickets:
        payment = getattr(t, 'payment', None)  # safely get payment, returns None if doesn't exist
        status = "Paid" if payment and payment.status == "success" else "Pending"
        total_earned += t.fare if status == "Paid" else 0

        text = f"Ticket: {t.ticket_number} | Passenger: {t.passenger.name} | Fare: {t.fare}/- | Status: {status}"
        p.drawString(50, y, text)
        y -= 20

        if y < 50:  # New page if space runs out
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 12)

    # Total money collected
    p.drawString(50, y-20, f"Total Money Collected: {total_earned}/-")

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bus_{bus_obj.bus_number}_Tickets.pdf"'
    return response