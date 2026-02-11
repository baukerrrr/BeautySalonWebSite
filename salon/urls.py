from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('book/<int:master_id>/<str:time_str>/<str:date_str>/', views.book, name='book'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
]