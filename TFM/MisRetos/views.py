from django.shortcuts import render


def registrarse(request):
    render(request, "MisRetos/registro.html")
