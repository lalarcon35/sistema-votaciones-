from django.contrib import admin
from .models import Categoria, Participante, Voto
from django.utils.html import format_html

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')
    
@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'categoria', 'detalles', 'mostrar_foto')
    list_filter = ('categoria',)
    
    @admin.display(description='Foto')
    def mostrar_foto(self, obj):
        if obj.foto:
            return format_html('<img src="{}"/>', obj.foto.url)
        return 'Sin foto'
    
@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'categoria', 'participante', 'fecha_voto')
    readonly_fields = ('usuario', 'categoria', 'participante', 'fecha_voto')
