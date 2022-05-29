from django.shortcuts import render


def registrarse(request):
    return render(request, "YoPuedo/registro.html")
