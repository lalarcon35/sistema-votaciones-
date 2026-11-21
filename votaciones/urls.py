from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name='votaciones'

urlpatterns = [
    path('tarjeton/', views.tarjeton_votacion, name='tarjeton'),
    path('api/categorias/',views.api_categorias_get, name='api_categorias'),
    path('panel/categorias/', views.panel_categorias, name='panel_categorias'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('panel/categorias/nueva/', views.crear_categoria, name='crear_categoria'),
    path('panel/participantes/', views.lista_participantes, name='lista_participantes'),
    path('panel/participantes/nuevo/', views.crear_participante, name='crear_participante'),
    path('panel/participantes/informe/', views.descargar_informe_participantes, name='descargar_informe_participantes'),
    path('panel/participantes/informe/ver/', views.ver_informe_participantes, name='ver_informe_participantes'),
    path('panel/categorias/', views.panel_categorias, name='panel_categorias')
]