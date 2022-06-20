from django.shortcuts import render
from . import utils
from .forms import registro


def registrarse(request):
    if request.method == 'GET':
        form = registro()

    else:
        form = registro(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            nombre = form.cleaned_data['nombre']
            password = form.cleaned_data['contraseña']
            password2 = form.cleaned_data['repetir_contraseña']
            foto_perfil = form['foto_perfil']

            if foto_perfil.filename:
                utils.guardar_fichero(foto_perfil)

    return render(request, "YoPuedo/registro.html", {'register_form': form})
