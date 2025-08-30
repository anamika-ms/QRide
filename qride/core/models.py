from django.db import models
from decimal import Decimal
import qrcode
from io import BytesIO
from django.core.files import File

class registration(models.Model):
    ROLE_CHOICES = [
        ('Passenger', 'Passenger'),
        ('Student', 'Student'),
        ('Operator', 'Operator'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"
    
class bus(models.Model):
    operator = models.ForeignKey(registration, on_delete=models.CASCADE, limit_choices_to={'role': 'Operator'})
    phone = models.CharField(max_length=15)
    bus_number = models.CharField(max_length=50, unique=True)
    bus_route = models.CharField(max_length=200)
    seat_capacity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='bus_qrcodes/', blank=True, null=True)
    

    def save(self, *args, **kwargs):
        creating = self._state.adding  # True if this is a new object
        super().save(*args, **kwargs)  # Save first to get ID

        if creating:  # Only generate QR when creating a new bus
            qr_data = f"https://yourdomain.com/start-ride/?bus={self.id}"
            qr_img = qrcode.make(qr_data)
            qr_io = BytesIO()
            qr_img.save(qr_io, format='PNG')
            self.qr_code.save(f"bus_{self.id}.png", File(qr_io), save=False)
            super().save(update_fields=['qr_code'])

    def __str__(self):
        return f"{self.bus_number} - {self.bus_route}"



class route(models.Model):
    bus = models.ForeignKey('Bus', on_delete=models.CASCADE, related_name='routes')
    operator = models.CharField(max_length=100)
    bus_number = models.CharField(max_length=20)
    start_stop = models.CharField(max_length=100)
    end_stop = models.CharField(max_length=100)
    distance = models.DecimalField(max_digits=6, decimal_places=2)
    fare = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('1.00'))
    total = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Fetch operator and bus number automatically
        if self.bus:
            self.operator = self.bus.operator.name
            self.bus_number = self.bus.bus_number

        # Convert values to Decimal before multiplying
        distance_value = Decimal(self.distance)
        fare_value = Decimal(self.fare)
        self.total = distance_value * fare_value

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.start_stop} → {self.end_stop} ({self.bus_number})"
