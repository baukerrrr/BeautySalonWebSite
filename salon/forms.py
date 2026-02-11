from django import forms
from .models import Client

class BookingForm(forms.Form):
    name = forms.CharField(label="Ваше Имя", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(label="Телефон", max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 777 777 77 77'}))