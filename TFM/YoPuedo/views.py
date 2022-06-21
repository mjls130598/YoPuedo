import logging
import os
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
            foto = request.FILES["foto_de_perfil"]
            fichero, extension = os.path.splitext(foto.name)
            localizacion = f'media/foto_perfil/{email}{extension}'
            utils.handle_uploaded_file(foto, localizacion)
            logger.info("Válido el formulario")

        else:
            logger.error("Error al validar el formulario")

    return render(request, "YoPuedo/registro.html", {'register_form': form})
