from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm, RegistroVeterinarioForm, RegistroDuenoForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .models import Intervencion, Animal
from .forms import IntervencionForm

def login_view(request):
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST

    formulario = LoginForm(datosFormulario)

    if request.method == "POST":
        if formulario.is_valid():
            username = formulario.cleaned_data.get('username')
            password = formulario.cleaned_data.get('password')
            usuario = authenticate(request, username=username, password=password)
            if usuario is not None:
                login(request, usuario)
                messages.success(request, "Has iniciado sesión correctamente")
                return redirect('index')
            else:
                messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, 'login.html', {"formulario": formulario})


def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente")
    return redirect('login')


def registro_veterinario_view(request):
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST

    formulario = RegistroVeterinarioForm(datosFormulario)

    if request.method == "POST":
        if formulario.is_valid():
            usuario = formulario.save()
            grupo = Group.objects.get(name='Veterinarios')
            usuario.groups.add(grupo)
            messages.success(request, "Veterinario registrado correctamente")
            return redirect('login')

    return render(request, 'registro_veterinario.html', {"formulario": formulario})


def registro_dueno_view(request):
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST

    formulario = RegistroDuenoForm(datosFormulario)

    if request.method == "POST":
        if formulario.is_valid():
            usuario = formulario.save()
            grupo = Group.objects.get(name='Dueños')
            usuario.groups.add(grupo)
            messages.success(request, "Dueño registrado correctamente")
            return redirect('login')

    return render(request, 'registro_dueno.html', {"formulario": formulario})


def index_view(request):
    return render(request, 'index.html')

@login_required
def intervencion_crear_view(request):
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST

    formulario = IntervencionForm(datosFormulario)

    if request.method == "POST":
        if formulario.is_valid():
            # Guardamos sin commit para poder asignar el veterinario
            intervencion = formulario.save(commit=False)
            # Asignamos automaticamente el veterinario responsable
            intervencion.veterinario_responsable = request.user
            intervencion.save()
            # Guardamos las relaciones ManyToMany de animales
            formulario.save_m2m()
            messages.success(request, 'Intervención creada correctamente')
            return redirect('intervencion_lista')

    return render(request, 'intervencion_crear.html', {"formulario": formulario})


@login_required
def intervencion_lista_view(request):
    # El veterinario solo ve sus intervenciones
    if request.user.groups.all()[0].name == 'Veterinarios':
        intervenciones = Intervencion.objects.filter(
            veterinario_responsable=request.user
        )
    # El dueño solo ve las intervenciones de sus animales
    else:
        intervenciones = Intervencion.objects.filter(
            animales__dueño=request.user
        ).distinct()

    return render(request, 'intervencion_lista.html', {"intervenciones": intervenciones})


@login_required
def intervencion_editar_view(request, intervencion_id):
    intervencion = Intervencion.objects.get(id=intervencion_id)

    # Solo el veterinario responsable puede editar
    if intervencion.veterinario_responsable != request.user:
        messages.error(request, 'No tienes permiso para editar esta intervención')
        return redirect('intervencion_lista')

    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST

    formulario = IntervencionForm(datosFormulario, instance=intervencion)

    if request.method == "POST":
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Intervención editada correctamente')
            return redirect('intervencion_lista')

    return render(request, 'intervencion_editar.html', {
        "formulario": formulario,
        "intervencion": intervencion
    })


@login_required
def intervencion_eliminar_view(request, intervencion_id):
    intervencion = Intervencion.objects.get(id=intervencion_id)

    # Solo el veterinario responsable puede eliminar
    if intervencion.veterinario_responsable != request.user:
        messages.error(request, 'No tienes permiso para eliminar esta intervención')
        return redirect('intervencion_lista')

    try:
        intervencion.delete()
        messages.success(request, 'Intervención eliminada correctamente')
    except:
        messages.error(request, 'No se pudo eliminar la intervención')

    return redirect('intervencion_lista')


@login_required
def mis_animales_view(request):
    animales = Animal.objects.filter(dueño=request.user)
    return render(request, 'mis_animales.html', {"animales": animales})

from .forms import BusquedaAvanzadaForm
from django.db.models import Q

@login_required
def intervencion_buscar_view(request):

    if len(request.GET) > 0:
        formulario = BusquedaAvanzadaForm(request.GET)

        if formulario.is_valid():
            texto = formulario.cleaned_data.get('texto')
            fecha_desde = formulario.cleaned_data.get('fecha_desde')
            fecha_hasta = formulario.cleaned_data.get('fecha_hasta')
            nivel_riesgo_minimo = formulario.cleaned_data.get('nivel_riesgo_minimo')
            animales = formulario.cleaned_data.get('animales')
            solo_no_completadas = formulario.cleaned_data.get('solo_no_completadas')

            # Restriccion de seguridad segun rol
            if request.user.groups.all()[0].name == 'Veterinarios':
                QSintervenciones = Intervencion.objects.filter(
                    veterinario_responsable=request.user
                )
            else:
                QSintervenciones = Intervencion.objects.filter(
                    animales__dueño=request.user
                ).distinct()

            # Filtro por texto
            if texto:
                QSintervenciones = QSintervenciones.filter(
                    Q(nombre__contains=texto) | Q(descripcion__contains=texto)
                )

            # Filtro por fecha desde
            if fecha_desde:
                QSintervenciones = QSintervenciones.filter(
                    fecha_programada__gte=fecha_desde
                )

            # Filtro por fecha hasta
            if fecha_hasta:
                QSintervenciones = QSintervenciones.filter(
                    fecha_programada__lte=fecha_hasta
                )

            # Filtro por nivel de riesgo
            if nivel_riesgo_minimo is not None:
                QSintervenciones = QSintervenciones.filter(
                    nivel_riesgo__gt=nivel_riesgo_minimo
                )

            # Filtro por animales
            if animales:
                QSintervenciones = QSintervenciones.filter(
                    animales__in=animales
                ).distinct()

            # Filtro por no completadas
            if solo_no_completadas:
                QSintervenciones = QSintervenciones.filter(
                    completada=False
                )

            intervenciones = QSintervenciones.all()

            return render(request, 'intervencion_buscar.html', {
                "formulario": formulario,
                "intervenciones": intervenciones
            })

    else:
        formulario = BusquedaAvanzadaForm(None)

    return render(request, 'intervencion_buscar.html', {"formulario": formulario})