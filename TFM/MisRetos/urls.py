from django.urls import path
from . import views

urlpatterns = [
    path('registrarse/', views.registrarse, name="registrarse")
]
