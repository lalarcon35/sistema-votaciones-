from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroUsuarioForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Usuario creado correctamente')
            return redirect('login')
    else: 
        form = RegistroUsuarioForm()
    return render(request, 'usuarios/registro.html',{'form': form})
# Create your views here.

@login_required
def inicio(request):
    return render(request, 'votaciones/tarjeton.html')

class LoginInteligente(LoginView):
    template_name = 'usuarios/login.html'

    def get_success_url(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return reverse_lazy('admin:index')
        
        # EL CAMBIO ESTÁ AQUÍ: Agrega 'votaciones:' antes de 'tarjeton'
        return reverse_lazy('votaciones:tarjeton')