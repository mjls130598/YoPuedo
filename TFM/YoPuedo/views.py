import logging
import os
from django.shortcuts import render
from . import utils
from .forms import RegistroForm
from TFM.settings import BASE_DIR

logger = logging.getLogger(__name__)


def registrarse(request):

    activar_modal = False
    if request.method == 'GET':
        logger.info("Entramos a la parte GET de REGISTRO")
        form = RegistroForm()

    else:
        logger.info("Entramos a la parte POST de REGISTRO")
        form = RegistroForm(request.POST, request.FILES)

        if form.is_valid():
            logger.info("Válido el formulario")
            email = form.cleaned_data['email']
            # utils.enviar_correo(email)
            activar_modal = True
        else:
            logger.error("Error al validar el formulario")

    return render(request, "YoPuedo/registro.html", {'register_form': form,
                                                     'activar_modal': activar_modal})


def entrar_aplicacion(request):
    if request.method == 'POST':
        logger.info("Entramos en la aplicación")
