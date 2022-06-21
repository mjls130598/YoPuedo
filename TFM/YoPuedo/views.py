import logging
from django.shortcuts import render
from . import utils
from .forms import registro

logger = logging.getLogger(__name__)


def registrarse(request):
    if request.method == 'GET':
        logger.info("Entramos a la parte GET de REGISTRO")
        form = registro()

    else:
        logger.info("Entramos a la parte POST de REGISTRO")

        form = registro(request.POST, request.FILES)

        if form.is_valid():
            email = form.cleaned_data['email']
            nombre = form.cleaned_data['nombre']
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['password_again']
            foto = request.FILES["foto_de_perfil"]

            utils.handle_uploaded_file(foto, email)

            logger.info("Válido el formulario")

    return render(request, "YoPuedo/registro.html", {'register_form': form})
