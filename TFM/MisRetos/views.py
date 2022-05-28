from django.shortcuts import render


def registrarse(request):
    return render(request, "MisRetos/registro.html")
