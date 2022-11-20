from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
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
    path('nuevo_reto/', views.nuevo_reto, name="nuevo_reto"),
    path('amigos/', views.get_amigos, name="amigos")
]
