from django.contrib import admin
from .models import Master, Client, Appointment

# Регистрируем модели, чтобы они появились в админке
admin.site.register(Master)
admin.site.register(Client)
admin.site.register(Appointment)