import logging
import os
from django.shortcuts import render
from . import utils
from .forms import RegistroForm
from TFM.settings import BASE_DIR

logger = logging.getLogger(__name__)


def registrarse(request):
    if request.method == 'GET':
        logger.info("Entramos a la parte GET de REGISTRO")
        form = RegistroForm()

    else:
        logger.info("Entramos a la parte POST de REGISTRO")
        form = RegistroForm(request.POST, request.FILES)

        if form.is_valid():
            email = form.cleaned_data['email'].value()
            nombre = form.cleaned_data['nombre'].value()
            password = form.cleaned_data['password'].value()
            foto = request.FILES["foto_de_perfil"]
            fichero, extension = os.path.splitext(foto.name)
            directorio = os.path.join(BASE_DIR, "media", "YoPuedo", "foto_perfil")
            localizacion = os.path.join(directorio, email + extension)
            try:
                utils.handle_uploaded_file(foto, localizacion, directorio)
            except:
                logger.error("Error al subir la foto de perfil")

            logger.info("Válido el formulario")

        else:
            logger.error("Error al validar el formulario")

    return render(request, "YoPuedo/registro.html", {'register_form': form})
