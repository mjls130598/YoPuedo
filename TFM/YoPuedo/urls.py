from django.urls import path
from . import views

urlpatterns = [
    path('registrarse/', views.registrarse, name="registrarse"),
    path('validar_clave/<str:tipo>/<str:email>', views.validar_clave,
         name="validar_clave"),
    path('iniciar_sesion/', views.iniciar_sesion, name="iniciar_sesion"),
]
