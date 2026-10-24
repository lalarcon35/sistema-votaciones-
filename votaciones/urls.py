from django.urls import path
from . import views

app_name='votaciones'

urlpatterns = [
    path('tarjeton/', views.tarjeton_votacion, name='tarjeton'),
]