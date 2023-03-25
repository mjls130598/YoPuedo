from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name="index"),
    path('registrarse/', views.registrarse, name="registrarse"),
    path('validar_clave/<str:tipo>/<str:email>', views.validar_clave,
         name="validar_clave"),
    path('iniciar_sesion/', views.iniciar_sesion, name="iniciar_sesion"),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='YoPuedo/recuperacion_contrasena/recuperacion_contrasena.html',
        html_email_template_name='YoPuedo/envio_correos/envio_recuperar_contrasena.html',
    ), name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='YoPuedo/recuperacion_contrasena/recuperacion_contrasena_enviado.html'
    ), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='YoPuedo/recuperacion_contrasena/nueva_contrasena.html',
    ), name="password_reset_confirm"),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='YoPuedo/recuperacion_contrasena/recuperacion_done.html',
    ), name="password_reset_complete"),
    path('mis_retos/', views.mis_retos, name="mis_retos"),
    path('retos', views.get_retos, name="retos"),
    path('reto/<str:id_reto>', views.get_reto, name="reto"),
    path('nuevo_reto/', views.nuevo_reto, name="nuevo_reto"),
    path('iniciar_reto/<str:id_reto>', views.iniciar_reto, name="iniciar_reto"),
    path('editar_reto/<str:id_reto>', views.editar_reto, name="editar_reto"),
    path('eliminar_reto/<str:id_reto>', views.eliminar_reto, name="eliminar_reto"),
    path('coordinador_reto/<str:id_reto>', views.coordinador_reto,
         name="coordinador_reto"),
    path('animador_reto/<str:id_reto>', views.animador_reto, name="animador_reto"),
    path('amigos/', views.get_amigos, name="amigos"),
    path('calificar/<str:id_etapa>', views.calificar_etapa, name="calificar"),
    path('prueba/<str:id_etapa>', views.pruebas, name="pruebas"),
    path('animos/<str:id_etapa>', views.animos, name='animos'),
    path('mi_perfil/', views.mi_perfil, name='mi_perfil'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('eliminar/', views.eliminar, name='eliminar'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('mis_amigos/', views.mis_amigos, name='mis_amigos'),
    path('nuevos_amigos/', views.nuevos_amigos, name="nuevos_amigos"),
]
