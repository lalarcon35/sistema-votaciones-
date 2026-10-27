from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Categoria, Participante, Voto

@login_required
def tarjeton_votacion(request):
    categorias = Categoria.objects.all()

    if request.method == 'POST':
        # Recorremos cada categoría para ver qué opción seleccionó el usuario
        for categoria in categorias:
            # Captura el valor del input radio (el ID del participante)
            participante_id = request.POST.get(f'participante_{categoria.pk}')
            
            if participante_id:
                participante = Participante.objects.get(pk=participante_id)
                
                # Creamos y guardamos el registro en la base de datos
                Voto.objects.create(
                    usuario=request.user,  # Nota: Si en tu modelo se llama 'user', cámbialo por user=request.user
                    categoria=categoria,
                    participante=participante
                )
        
        # Después de guardar, recargamos la página o redirigimos a una vista de éxito
        return redirect('votaciones:tarjeton')

    return render(request, 'votaciones/tarjeton.html', {'categorias': categorias})