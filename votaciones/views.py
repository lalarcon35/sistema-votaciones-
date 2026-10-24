from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Categoria, Participante, Voto

@login_required
def tarjeton_votacion(request):
    # 1. Si el usuario presiona "Enviar Votos" (Lógica de guardado)
    if request.method == 'POST':
        for nombre_input, id_participante in request.POST.items():
            if nombre_input.startswith('categoria_'):
                id_categoria = nombre_input.split('_')[1]
                
                categoria = Categoria.objects.get(id=id_categoria)
                participante = Participante.objects.get(id=id_participante)
                
                # Guarda el voto asociándolo al usuario actual
                Voto.objects.get_or_create(
                    usuario=request.user,
                    categoria=categoria,
                    defaults={'participante': participante}
                )
        return redirect('votaciones:tarjeton')

    # 2. Si el usuario apenas entra a la página (Lógica de visualización)
    # Identificamos en qué categorías ya votó este usuario para ocultárselas y evitar trampa
    categorias_votadas = Voto.objects.filter(usuario=request.user).values_list('categoria_id', flat=True)
    categorias_disponibles = Categoria.objects.filter(activa=True).exclude(id__in=categorias_votadas)
    
    return render(request, 'votaciones/tarjeton.html', {
        'categorias': categorias_disponibles
    })