from django.contrib import admin
from .models import Categoria, Participante, Voto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')
    
@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'categoria', 'detalles')
    list_filter = ('categoria',)
    
@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'categoria', 'participante', 'fecha_voto')
    readonly_fields = ('usuario', 'categoria', 'participante', 'fecha_voto')
