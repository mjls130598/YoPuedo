import logging
from django.shortcuts import render
from . import utils
from .forms import registro

logger = logging.getLogger(__name__)


def registrarse(request):
    if request.method == 'GET':
        form = registro()

    else:
        form = registro(request.POST, request.FILES)
        foto_perfil = request.FILES.get('foto_de_perfil')

        if form.is_valid() and utils.checkear_imagen(foto_perfil):
            email = form.cleaned_data['email']
            nombre = form.cleaned_data['nombre']
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['password_again']

            logger.info("Válido el formulario")

    return render(request, "YoPuedo/registro.html", {'register_form': form})
