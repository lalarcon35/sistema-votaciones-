from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns =  [
    # RF-01 Registro de usuarios
    path('registro/', views.registro, name='registro'),
     # RF-02 inicio y cierre de sesion
    path('login/', LoginView.as_view(template_name='usuarios/login.html'),name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout')
]