from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.hashers import make_password

class registration(models.Model):
    ROLE_CHOICES = [
        ('passenger', 'Passenger'),
        ('student', 'Student'),
        ('operator', 'Bus Operator'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"

