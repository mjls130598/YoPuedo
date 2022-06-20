from django.shortcuts import render
from .forms import registro


def registrarse(request):
    if request.method == 'GET':
        form = registro()

    else:
        form = registro(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            nombre = form.cleaned_data['nombre']
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['password_again']
            foto_perfil = form['foto_de_perfil']

            render(request, "google.es")

    return render(request, "YoPuedo/registro.html", {'register_form': form})
