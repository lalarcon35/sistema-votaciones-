from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Categoria, Participante, Voto
from django.http import JsonResponse
from django.contrib import messages

@login_required
def tarjeton_votacion(request):
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        for categoria in categorias:
            participante_id = request.POST.get(f'participante_{categoria.id}')
            
            if participante_id:
                ya_voto = Voto.objects.filter(usuario=request.user, categoria=categoria).exists()
                
                if ya_voto:
                    messages.warning(request, f"Ya tienes un registro en la categoría {categoria.nombre}.")
                else:
                    try:
                        participante = Participante.objects.get(id=participante_id)
                        Voto.objects.create(
                            usuario=request.user,
                            categoria=categoria,
                            participante=participante
                        )
                        messages.success(request, f"¡Tu voto para {categoria.nombre} se guardó correctamente!")
                    except Participante.DoesNotExist:
                        messages.error(request, f"Ocurrió un error al procesar tu voto.")
        
        return redirect('votaciones:tarjeton')

    # Si es una petición GET normal (cuando apenas entras o te logueas), solo muestra la página limpia
    return render(request, 'votaciones/tarjeton.html', {'categorias': categorias})
def  api_categorias_get(request):
    if request.method == 'GET':
        categorias = Categoria.objects.filter(activa=True)
        data = []
        
        for categoria in categorias:
            opciones = list(categoria.participantes.values('id','nombre_completo','detalles'))
            
            data.append({
                'id': categoria.id,
                'nombre': categoria.nombre,
                'descripcion':opciones
            })  
        return JsonResponse({'categorias':data}, safe=False)
      
    