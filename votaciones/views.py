from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from  django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Categoria, Participante, Voto
from django.http import JsonResponse
from django.contrib import messages
from .forms import CategoriaForm, ParticipanteForm
from django.shortcuts import get_object_or_404, render

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

@staff_member_required(login_url='/admin/login/')
def panel_categorias(request):
    categorias = Categoria.objects.annotate(
        total_participantes=Count('participantes', distinct=True),
        total_votos=Count('voto', distinct=True),
    )

    context = {
        'categorias': categorias,
        'total_categorias': Categoria.objects.count(),
        'total_participantes': Participante.objects.count(),
        'total_votos': Voto.objects.count(),
    }
    return render(request, 'votaciones/admin_categorias.html', context)

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
      
@staff_member_required(login_url='/admin/login/')
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('votaciones:panel_categorias')
    else:
        form = CategoriaForm()

    return render(request, 'votaciones/crear_categoria.html', {'form': form})

@staff_member_required(login_url='/admin/login/')
def lista_participantes(request):
    categoria_id = request.GET.get('categoria')
    participantes = Participante.objects.select_related('categoria').annotate(
        total_votos=Count('voto', distinct=True)
    )

    categoria_seleccionada = None
    if categoria_id:
        categoria_seleccionada = get_object_or_404(Categoria, pk=categoria_id)
        participantes = participantes.filter(categoria=categoria_seleccionada)

    context = {
        'participantes': participantes,
        'categorias': Categoria.objects.all(),
        'categoria_seleccionada': categoria_seleccionada,
        'total_categorias': Categoria.objects.count(),
        'total_participantes': Participante.objects.count(),
        'total_votos': Voto.objects.count(),
    }
    return render(request, 'votaciones/participantes.html', context)

@staff_member_required(login_url='/admin/login/')
def crear_participante(request):
    initial = {}
    if request.GET.get('categoria'):
        initial['categoria'] = request.GET.get('categoria')

    if request.method == 'POST':
        form = ParticipanteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('votaciones:lista_participantes')
    else:
        form = ParticipanteForm(initial=initial)

    return render(request, 'votaciones/form_participante.html', {'form': form})

@staff_member_required(login_url='/admin/login/')
def descargar_informe_participantes(request):
    categoria_id = request.GET.get('categoria')
    participantes = Participante.objects.select_related('categoria').annotate(
        total_votos=Count('voto', distinct=True)
    ).order_by('-total_votos', 'nombre_completo')

    nombre_archivo = 'informe_participantes.csv'
    if categoria_id:
        categoria = get_object_or_404(Categoria, pk=categoria_id)
        participantes = participantes.filter(categoria=categoria)
        nombre_archivo = f'informe_{categoria.nombre.lower().replace(" ", "_")}.csv'

    total_votos = sum(p.total_votos for p in participantes)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    response.write('\ufeff')  # BOM para que Excel abra tildes y eñes correctamente

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Puesto', 'Participante', 'Categoría', 'Votos', 'Porcentaje (%)', 'Detalles'])

    for idx, p in enumerate(participantes, start=1):
        porcentaje = round((p.total_votos / total_votos) * 100, 1) if total_votos > 0 else 0
        writer.writerow([
            idx,
            p.nombre_completo,
            p.categoria.nombre,
            p.total_votos,
            f'{porcentaje}%',
            p.detalles or '',
        ])

    return response

@staff_member_required(login_url='/admin/login/')
def ver_informe_participantes(request):
    categoria_id = request.GET.get('categoria')
    participantes = Participante.objects.select_related('categoria').annotate(
        total_votos=Count('voto', distinct=True)
    ).order_by('-total_votos', 'nombre_completo')

    categoria_seleccionada = None
    if categoria_id:
        categoria_seleccionada = get_object_or_404(Categoria, pk=categoria_id)
        participantes = participantes.filter(categoria=categoria_seleccionada)

    votos_mostrados = sum(p.total_votos for p in participantes)
    for p in participantes:
        p.porcentaje = round((p.total_votos / votos_mostrados) * 100, 1) if votos_mostrados > 0 else 0

    return render(request, 'votaciones/informe_participantes.html', {
        'participantes': participantes,
        'categoria_seleccionada': categoria_seleccionada,
        'votos_mostrados': votos_mostrados,
        'total_categorias': Categoria.objects.count(),
    })