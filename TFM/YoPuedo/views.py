import logging

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from .utils import Utils
from .forms import RegistroForm, InicioForm
from .models import Usuario

logger = logging.getLogger(__name__)
utils = Utils()


def registrarse(request):
    if request.method == 'GET':
        logger.info("Entramos a la parte GET de REGISTRO")
        form = RegistroForm()

    else:
        logger.info("Entramos a la parte POST de REGISTRO")
        form = RegistroForm(request.POST, request.FILES)

        if form.is_valid():
            logger.info("Válido el formulario")
            logger.info("Mandamos a guardar el usuario (temporalmente)")
            email = form.cleaned_data['email'].value()
            password = form.cleaned_data['password'].value()
            clave_aleatoria, clave_fija = utils.guardar_usuario(utils, request)
            utils.enviar_clave(clave_aleatoria, email)
            utils.enviar_clave_fija(clave_fija, email)

            user = authenticate(request, username=email, password=password)
            login(request, user)
            return render(request, "YoPuedo/peticion-clave.html", {'email': email,
                                                                   'contador': 0,
                                                                   'errors': [],
                                                                   'tipo': 'registro'})
        else:
            logger.error("Error al validar el formulario")

    return render(request, "YoPuedo/registro.html", {'register_form': form})


def iniciar_sesion(request):
    if request.method == 'GET':
        logger.info("Entramos a la parte GET de INICIAR SESIÓN")
        form = InicioForm()

    else:
        logger.info("Entramos a la parte POST de INICIAR SESIÓN")
        form = InicioForm(request.POST)

        if form.is_valid():
            logger.info("Válido el formulario")
            email = form.cleaned_data['email_sesion'].value()
            password = form.cleaned_data['password_sesion'].value()
            clave_aleatoria = utils.claves_aleatorias(10)
            utils.enviar_clave(clave_aleatoria, email)

            user = authenticate(request, username=email, password=password)
            login(request, user)
            return render(request, "YoPuedo/peticion-clave.html", {'email': email,
                                                                   'contador': 0,
                                                                   'errors': [],
                                                                   'tipo': 'inicio'})
        else:
            logger.error("Error al validar el formulario")

    return render(request, "YoPuedo/iniciar_sesion.html", {'inicio_form': form})


def validar_clave(request):
    if request.method == 'POST':
        logger.info("Comprobamos si la clave introducida es la correcta")

        email = request['POST'].get('email')
        contador = request['POST'].get('contador')
        tipo = request['POST'].get('tipo')
        clave_aleatoria = request['POST'].get('clave')

        usuario = Usuario.objects.get(email=email)

        clave_fija_usuario = usuario.clave_fija
        clave_aleatoria_usuario = usuario.clave_aleatoria

        if clave_aleatoria != clave_fija_usuario and clave_aleatoria != \
                clave_aleatoria_usuario:
            if contador < 2:
                logger.info(f"Intento nº {contador - 1}")
                error = 'La clave introducida no es la correcta. Inténtelo de nuevo'
                return render(request, "YoPuedo/peticion-clave.html",
                              {'email': email, 'contador': contador + 1,
                               'errors': [error]})
            else:
                if tipo == 'registro':
                    logger.info("Eliminamos usuario y mandamos al usuario a que se "
                                "registre de nuevo")
                    usuario.delete()
                    form = RegistroForm()
                    form.add_error('email', 'Error al introducir el código de '
                                            'verificación. Regístrese de nuevo en '
                                            'nuestra aplicación')
                    return render(request, "YoPuedo/registro.html",
                                  {'register_form': form})

        else:
            logger.info("Validación correcta")
            logout(request)
            form = RegistroForm()
            return render(request, "YoPuedo/registro.html", {'register_form': form})
