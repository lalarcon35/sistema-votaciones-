from django.db import models
from django.conf import settings

class Edicion(models.Model):
    nombre = models.CharField(max_length=150)  # Ej: "60° Festival de la Leyenda (2026)"
    anio = models.PositiveIntegerField()
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['-anio', '-id']

    def __str__(self):
        return self.nombre
    
class Categoria(models.Model):
    edicion = models.ForeignKey(
        Edicion,
        on_delete=models.CASCADE,
        related_name='categorias',
        null=True,
        blank=True,
    )
    nombre = models.CharField(max_length=150, help_text="Ej: Acordeonero Profesional, Canción Inédita")
    descripcion = models.TextField(blank=True, null=True, help_text="Breve descripción de la categoría")
    activa = models.BooleanField(default=True, help_text="Desmarcar para cerrar las votaciones de esta categoría")  
    
    def __str__(self):
        return self.nombre

class Participante(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='participantes')
    nombre_completo = models.CharField(max_length=200)
    detalles = models.CharField(max_length=200, blank=True, null=True, help_text="Ej: Ciudad de origen, o nombre de la canción inédita")
    foto = models.ImageField(upload_to='participantes/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_completo} - {self.categoria.nombre}"

class Voto(models.Model):
    # Relaciona el voto con el usuario que inició sesión
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE, null=True)
    fecha_voto = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'categoria')

    def __str__(self):
        return f"Voto de {self.usuario.username} en {self.categoria.nombre}"
        
        
