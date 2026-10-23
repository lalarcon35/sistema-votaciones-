from django import forms
from .models import Usuario

class RegistroUsuarioForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nombres", 
        widget=forms.TextInput(attrs={'placeholder': 'Ingresa tus nombres'})
    )
    last_name = forms.CharField(
        label="Apellidos", 
        widget=forms.TextInput(attrs={'placeholder': 'Ingresa tus apellidos'})
    )
    email = forms.EmailField(
        label="Correo electrónico", 
        widget=forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'})
    )
    documento = forms.CharField(
        label="Número de documento", 
        widget=forms.TextInput(attrs={'placeholder': 'Numero de documento'})
    )
    telefono = forms.CharField(
        required=False, 
        label="Teléfono", 
        widget=forms.TextInput(attrs={'placeholder': 'Opcional'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingresa tu contraseña'})
    )
    password_confirm = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirma tu contraseña'})
    )

    class Meta:
        model = Usuario
        fields = (
            'first_name', 
            'last_name', 
            'email', 
            'documento', 
            'telefono'
        )

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if Usuario.objects.filter(documento=documento).exists():
            raise forms.ValidationError("Ya existe una cuenta registrada con este número de documento.")
        return documento

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta registrada con este correo electrónico.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user