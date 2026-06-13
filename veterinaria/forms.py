from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
import datetime
from .models import Intervencion, Tratamiento, Animal

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        required=True
    )
    password = forms.CharField(
        label="Contraseña",
        required=True,
        widget=forms.PasswordInput()
    )

class RegistroVeterinarioForm(UserCreationForm):
    numero_colegiado = forms.CharField(
        label="Número de Colegiado",
        required=True,
        max_length=50
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'numero_colegiado', 'password1', 'password2']

class RegistroDuenoForm(UserCreationForm):

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']

class IntervencionForm(forms.ModelForm):

    class Meta:
        model = Intervencion
        fields = [
            'nombre',
            'descripcion',
            'tratamiento',
            'animales',
            'nivel_riesgo',
            'fecha_programada',
            'fecha_fin_recuperacion',
            'completada',
        ]
        # No incluimos veterinario_responsable porque se asigna automaticamente
        widgets = {
            'fecha_programada': forms.SelectDateWidget(),
            'fecha_fin_recuperacion': forms.SelectDateWidget(),
            'descripcion': forms.Textarea(),
        }

    def clean(self):
        super().clean()

        nombre = self.cleaned_data.get('nombre')
        descripcion = self.cleaned_data.get('descripcion')
        tratamiento = self.cleaned_data.get('tratamiento')
        animales = self.cleaned_data.get('animales')
        nivel_riesgo = self.cleaned_data.get('nivel_riesgo')
        fecha_programada = self.cleaned_data.get('fecha_programada')
        fecha_fin_recuperacion = self.cleaned_data.get('fecha_fin_recuperacion')

        # Validacion 1: Nombre unico
        intervencionNombre = Intervencion.objects.filter(nombre=nombre).first()
        if intervencionNombre is not None:
            # Controlamos que en edicion no de error si el nombre es el mismo
            if self.instance is None or intervencionNombre.id != self.instance.id:
                self.add_error('nombre', 'Ya existe una intervención con ese nombre')

        # Validacion 2: Descripcion minimo 100 caracteres
        if descripcion and len(descripcion) < 100:
            self.add_error('descripcion', 'La descripción debe tener al menos 100 caracteres')

        # Validacion 3: Tratamiento apto para intervenciones
        if tratamiento and not tratamiento.apto_para_intervenciones:
            self.add_error('tratamiento', 'El tratamiento no es apto para intervenciones')

        # Validacion 4: Animales con al menos 6 meses de edad
        if animales:
            fechaLimite = datetime.date.today() - datetime.timedelta(days=6*30)
            for animal in animales:
                if animal.fecha_nacimiento > fechaLimite:
                    self.add_error('animales', f'El animal {animal.nombre} no tiene al menos 6 meses de edad')

        # Validacion 5: Nivel de riesgo entre 0 y 10
        if nivel_riesgo is not None:
            if nivel_riesgo < 0 or nivel_riesgo > 10:
                self.add_error('nivel_riesgo', 'El nivel de riesgo debe estar entre 0 y 10')

        # Validacion 6: fecha_programada menor que fecha_fin_recuperacion
        if fecha_programada and fecha_fin_recuperacion:
            if fecha_programada >= fecha_fin_recuperacion:
                self.add_error('fecha_programada', 'La fecha programada debe ser anterior a la fecha de fin de recuperación')

        # Validacion 7: fecha_fin_recuperacion igual o posterior a hoy
        if fecha_fin_recuperacion:
            if fecha_fin_recuperacion < datetime.date.today():
                self.add_error('fecha_fin_recuperacion', 'La fecha de fin de recuperación debe ser igual o posterior a hoy')

        return self.cleaned_data
    
class BusquedaAvanzadaForm(forms.Form):

    texto = forms.CharField(
        label="Texto en nombre o descripción",
        required=False
    )

    fecha_desde = forms.DateField(
        label="Fecha programada desde",
        required=False,
        widget=forms.SelectDateWidget(years=range(2020, 2030))
    )

    fecha_hasta = forms.DateField(
        label="Fecha programada hasta",
        required=False,
        widget=forms.SelectDateWidget(years=range(2020, 2030))
    )

    nivel_riesgo_minimo = forms.IntegerField(
        label="Nivel de riesgo mayor a",
        required=False
    )

    animales = forms.ModelMultipleChoiceField(
        queryset=Animal.objects.all(),
        label="Animales",
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )

    solo_no_completadas = forms.BooleanField(
        label="Solo intervenciones no completadas",
        required=False
    )

    def clean(self):
        super().clean()

        texto = self.cleaned_data.get('texto')
        fecha_desde = self.cleaned_data.get('fecha_desde')
        fecha_hasta = self.cleaned_data.get('fecha_hasta')
        nivel_riesgo_minimo = self.cleaned_data.get('nivel_riesgo_minimo')
        animales = self.cleaned_data.get('animales')
        solo_no_completadas = self.cleaned_data.get('solo_no_completadas')

        # Validacion: al menos un campo relleno
        if (not texto and
            not fecha_desde and
            not fecha_hasta and
            nivel_riesgo_minimo is None and
            not animales and
            not solo_no_completadas):
            self.add_error('texto', 'Debes introducir al menos un valor para buscar')

        # Validacion: fecha hasta mayor que fecha desde
        if fecha_desde and fecha_hasta:
            if fecha_hasta < fecha_desde:
                self.add_error('fecha_hasta', 'La fecha hasta debe ser mayor que la fecha desde')

        # Validacion: nivel de riesgo entre 0 y 10
        if nivel_riesgo_minimo is not None:
            if nivel_riesgo_minimo < 0 or nivel_riesgo_minimo > 10:
                self.add_error('nivel_riesgo_minimo', 'El nivel de riesgo debe estar entre 0 y 10')

        return self.cleaned_data