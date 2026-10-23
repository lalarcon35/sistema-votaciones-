from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroUsuarioForm

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
    return render(request, 'usuarios/inicio.html')