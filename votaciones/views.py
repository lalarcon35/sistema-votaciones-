import csv
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoriaForm, ParticipanteForm
from .models import Categoria, Edicion, Participante, Voto


def obtener_edicion_actual(request):
    ediciones = Edicion.objects.order_by('-anio', '-id')
    edicion_id = request.GET.get('edicion')

    if edicion_id:
        edicion = get_object_or_404(Edicion, pk=edicion_id)
        request.session['edicion_id'] = edicion.pk
        return edicion, ediciones

    sesion_id = request.session.get('edicion_id')
    if sesion_id:
        edicion = ediciones.filter(pk=sesion_id).first()
        if edicion:
            return edicion, ediciones

    edicion = ediciones.filter(activa=True).first() or ediciones.first()
    if edicion:
        request.session['edicion_id'] = edicion.pk
    return edicion, ediciones


@staff_member_required(login_url='/admin/login/')
def crear_edicion(request):
    error = None
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        anio = request.POST.get('anio', '').strip()
        activa = request.POST.get('activa') == 'on'

        if not nombre or not anio.isdigit():
            error = 'Debes ingresar un nombre de edición y un año válido.'
        else:
            if activa:
                Edicion.objects.filter(activa=True).update(activa=False)
            edicion = Edicion.objects.create(
                nombre=nombre,
                anio=int(anio),
                activa=activa,
            )
            request.session['edicion_id'] = edicion.pk
            return redirect('votaciones:panel_categorias')

    return render(request, 'votaciones/crear_edicion.html', {'error': error})


@login_required
@login_required
def tarjeton_votacion(request):
    edicion_actual, ediciones = obtener_edicion_actual(request)
    categorias = (
        Categoria.objects.filter(edicion=edicion_actual, activa=True)
        if edicion_actual
        else Categoria.objects.filter(activa=True)
    )

    if request.method == 'POST':
        if edicion_actual and not edicion_actual.activa:
            messages.error(request, "Esta edición del festival no está activa para votación.")
            return redirect('votaciones:tarjeton')

        for categoria in categorias:
            participante_id = request.POST.get(f'participante_{categoria.id}')

            if participante_id:
                ya_voto = Voto.objects.filter(usuario=request.user, categoria=categoria).exists()

                if ya_voto:
                    messages.warning(request, f"Ya tienes un registro en la categoría {categoria.nombre}.")
                else:
                    try:
                        participante = Participante.objects.get(id=participante_id, categoria=categoria)
                        Voto.objects.create(
                            usuario=request.user,
                            categoria=categoria,
                            participante=participante,
                        )
                        messages.success(request, f"¡Tu voto para {categoria.nombre} se guardó correctamente!")
                    except Participante.DoesNotExist:
                        messages.error(request, "Ocurrió un error al procesar tu voto.")

        return redirect('votaciones:tarjeton')

    return render(request, 'votaciones/tarjeton.html', {
        'categorias': categorias,
        'edicion_actual': edicion_actual,
        'ediciones': ediciones,
    })


@staff_member_required(login_url='/admin/login/')
def panel_categorias(request):
    edicion_actual, ediciones = obtener_edicion_actual(request)
    categorias_qs = (
        Categoria.objects.filter(edicion=edicion_actual)
        if edicion_actual
        else Categoria.objects.all()
    )

    categorias = categorias_qs.annotate(
        total_participantes=Count('participantes', distinct=True),
        total_votos=Count('voto', distinct=True),
    )

    participantes_qs = (
        Participante.objects.filter(categoria__edicion=edicion_actual)
        if edicion_actual
        else Participante.objects.all()
    )
    votos_qs = (
        Voto.objects.filter(categoria__edicion=edicion_actual)
        if edicion_actual
        else Voto.objects.all()
    )

    context = {
        'categorias': categorias,
        'edicion_actual': edicion_actual,
        'ediciones': ediciones,
        'total_categorias': categorias_qs.count(),
        'total_participantes': participantes_qs.count(),
        'total_votos': votos_qs.count(),
    }
    return render(request, 'votaciones/admin_categorias.html', context)


def api_categorias_get(request):
    if request.method == 'GET':
        edicion_actual, _ = obtener_edicion_actual(request)
        categorias = Categoria.objects.filter(activa=True)
        if edicion_actual:
            categorias = categorias.filter(edicion=edicion_actual)

        data = []
        for categoria in categorias:
            opciones = list(categoria.participantes.values('id', 'nombre_completo', 'detalles'))
            data.append({
                'id': categoria.id,
                'nombre': categoria.nombre,
                'descripcion': opciones,
            })
        return JsonResponse({'categorias': data}, safe=False)


@staff_member_required(login_url='/admin/login/')
def crear_categoria(request):
    edicion_actual, _ = obtener_edicion_actual(request)

    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            if edicion_actual and not getattr(categoria, 'edicion_id', None):
                categoria.edicion = edicion_actual
            categoria.save()
            return redirect('votaciones:panel_categorias')
    else:
        form = CategoriaForm()

    return render(request, 'votaciones/crear_categoria.html', {
        'form': form,
        'edicion_actual': edicion_actual,
    })


@staff_member_required(login_url='/admin/login/')
def lista_participantes(request):
    edicion_actual, ediciones = obtener_edicion_actual(request)
    categoria_id = request.GET.get('categoria')

    categorias_qs = (
        Categoria.objects.filter(edicion=edicion_actual)
        if edicion_actual
        else Categoria.objects.all()
    )
    participantes = Participante.objects.select_related('categoria').annotate(
        total_votos=Count('voto', distinct=True)
    )
    if edicion_actual:
        participantes = participantes.filter(categoria__edicion=edicion_actual)

    categoria_seleccionada = None
    if categoria_id:
        categoria_seleccionada = get_object_or_404(categorias_qs, pk=categoria_id)
        participantes = participantes.filter(categoria=categoria_seleccionada)

    context = {
        'participantes': participantes,
        'categorias': categorias_qs,
        'categoria_seleccionada': categoria_seleccionada,
        'edicion_actual': edicion_actual,
        'ediciones': ediciones,
        'total_categorias': categorias_qs.count(),
        'total_participantes': participantes.count(),
        'total_votos': Voto.objects.filter(categoria__edicion=edicion_actual).count() if edicion_actual else Voto.objects.count(),
    }
    return render(request, 'votaciones/participantes.html', context)


@staff_member_required(login_url='/admin/login/')
def crear_participante(request):
    edicion_actual, _ = obtener_edicion_actual(request)
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

    if edicion_actual and 'categoria' in form.fields:
        form.fields['categoria'].queryset = Categoria.objects.filter(edicion=edicion_actual)

    return render(request, 'votaciones/form_participante.html', {
        'form': form,
        'edicion_actual': edicion_actual,
    })


@staff_member_required(login_url='/admin/login/')
def descargar_informe_participantes(request):
    edicion_actual, _ = obtener_edicion_actual(request)
    categoria_id = request.GET.get('categoria')

    participantes = Participante.objects.select_related('categoria').annotate(
        total_votos=Count('voto', distinct=True)
    ).order_by('-total_votos', 'nombre_completo')

    if edicion_actual:
        participantes = participantes.filter(categoria__edicion=edicion_actual)

    nombre_archivo = 'informe_participantes.csv'
    if categoria_id:
        categoria = get_object_or_404(Categoria, pk=categoria_id)
        participantes = participantes.filter(categoria=categoria)
        nombre_archivo = f'informe_{categoria.nombre.lower().replace(" ", "_")}.csv'

    total_votos = sum(p.total_votos for p in participantes)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    response.write('\ufeff')

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
    edicion_actual, ediciones = obtener_edicion_actual(request)
    categoria_id = request.GET.get('categoria')

    participantes = Participante.objects.select_related('categoria').annotate(
        total_votos=Count('voto', distinct=True)
    ).order_by('-total_votos', 'nombre_completo')

    if edicion_actual:
        participantes = participantes.filter(categoria__edicion=edicion_actual)

    categoria_seleccionada = None
    if categoria_id:
        categoria_seleccionada = get_object_or_404(Categoria, pk=categoria_id)
        participantes = participantes.filter(categoria=categoria_seleccionada)

    votos_mostrados = sum(p.total_votos for p in participantes)
    for p in participantes:
        p.porcentaje = round((p.total_votos / votos_mostrados) * 100, 1) if votos_mostrados > 0 else 0

    total_categorias = (
        Categoria.objects.filter(edicion=edicion_actual).count()
        if edicion_actual
        else Categoria.objects.count()
    )

    return render(request, 'votaciones/informe_participantes.html', {
        'participantes': participantes,
        'categoria_seleccionada': categoria_seleccionada,
        'edicion_actual': edicion_actual,
        'ediciones': ediciones,
        'votos_mostrados': votos_mostrados,
        'total_categorias': total_categorias,
    })