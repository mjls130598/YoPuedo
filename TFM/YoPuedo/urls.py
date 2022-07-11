from django.urls import path
from . import views

urlpatterns = [
    path('registrarse/', views.registrarse, name="registrarse"),
    path('validar_clave/', views.validar_clave, name="validar_clave"),
]
