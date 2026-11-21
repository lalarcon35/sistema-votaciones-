from django import forms
from .models import Categoria, Participante


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activa']
        labels = {
            'nombre': 'Nombre de la categoría',
            'descripcion': 'Descripción',
            'activa': 'Categoría activa para votación',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej. Acordeonero Profesional, Canción Inédita',
                'autocomplete': 'off',
                'required': True,
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'rows': 4,
                'placeholder': 'Breve descripción de la categoría',
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'toggle-input',
            }),
        }

class ParticipanteForm(forms.ModelForm):
    class Meta:
        model = Participante
        fields = ['nombre_completo', 'categoria', 'detalles', 'foto']
        labels = {
            'nombre_completo': 'Nombre completo',
            'categoria': 'Categoría',
            'detalles': 'Detalles',
            'foto': 'Foto',
        }