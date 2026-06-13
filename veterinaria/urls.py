from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/veterinario/', views.registro_veterinario_view, name='registro_veterinario'),
    path('registro/dueno/', views.registro_dueno_view, name='registro_dueno'),
    path('intervenciones/', views.intervencion_lista_view, name='intervencion_lista'),
    path('intervenciones/crear/', views.intervencion_crear_view, name='intervencion_crear'),
    path('intervenciones/editar/<int:intervencion_id>/', views.intervencion_editar_view, name='intervencion_editar'),
    path('intervenciones/eliminar/<int:intervencion_id>/', views.intervencion_eliminar_view, name='intervencion_eliminar'),
    path('mis-animales/', views.mis_animales_view, name='mis_animales'),
    path('intervenciones/buscar/', views.intervencion_buscar_view, name='intervencion_buscar'),
]