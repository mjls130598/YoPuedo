import logging

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.template.loader import get_template

from .utils import Utils
from .forms import RegistroForm, InicioForm, ClaveForm
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
            nombre = form.cleaned_data['nombre'].value()
            password = form.cleaned_data['password'].value()
            foto = request.FILES["foto_de_perfil"]

            clave_aleatoria, clave_fija = utils.guardar_usuario(utils, email, nombre,
                                                                password, foto)
            enviar_clave(clave_aleatoria, email, "Registro en la aplicación Yo Puedo")
            enviar_clave_fija(clave_fija, email)

            user = authenticate(request, username=email, password=password)
            login(request, user)

            data = {'email': email, 'contador': 0, 'tipo': 'registro'}
            clave_form = ClaveForm(data)
            return render(request, "YoPuedo/peticion-clave.html", {'peticion_clave':
                                                                       clave_form})
        else:
            logger.error("Error al validar el formulario")

    return render(request, "YoPuedo/registro.html", {'register_form': form})


def enviar_clave(clave, email, contexto):
    template = get_template('YoPuedo/envio_clave.html')
    context = {
        'titulo': "¿Eres tú?",
        'contexto': contexto,
        'clave': clave
    }
    content = template.render(context)

    utils.enviar_correo(content, email, contexto)


def enviar_clave_fija(clave, email):
    template = get_template('YoPuedo/envio_clave_fija.html')
    context = {
        'clave': clave
    }
    content = template.render(context)

    utils.enviar_correo(content, email, "Bienvenido a Yo Puedo")


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
            enviar_clave(clave_aleatoria, email, "Inicio de sesión en la aplicación Yo "
                                                 "Puedo")

            user = authenticate(request, username=email, password=password)
            login(request, user)

            data = {'email': email, 'contador': 0, 'tipo': 'inicio_sesion'}
            clave_form = ClaveForm(data)
            return render(request, "YoPuedo/peticion-clave.html", {'peticion_clave':
                                                                       clave_form})
        else:
            logger.error("Error al validar el formulario")

    return render(request, "YoPuedo/iniciar_sesion.html", {'inicio_form': form})


def validar_clave(request):
    if request.method == 'POST':
        logger.info("Comprobamos si la clave introducida es la correcta")

        clave_form = ClaveForm(request.POST)

        contador = clave_form.cleaned_data['contador']
        tipo = clave_form.cleaned_data['tipo']
        email = clave_form.cleaned_data['email']

        if clave_form.is_valid():
            if tipo == 'registro' or tipo == 'inicio_sesion':
                logger.info("Iniciamos sesión")
                form = RegistroForm()
                return render(request, "YoPuedo/registro.html", {'register_form': form})

        else:
            if contador < 2:
                logger.info(f"Intento nº {contador + 1}")
                clave_form.cleaned_data['contador'] = contador + 1
                return render(request, "YoPuedo/peticion-clave.html",
                              {'peticion_clave': clave_form})
            else:
                logout(request)
                if tipo == 'registro' or tipo == 'inicio sesión':
                    logger.info("Mandamos a la página de registro")

                    if tipo == 'registro':
                        Usuario.objects.get(email=email).delete()

                    form = RegistroForm()
                    form.add_error('email', 'Error al introducir el código de '
                                            'verificación. Regístrese de nuevo en '
                                            'nuestra aplicación')
                    return render(request, "YoPuedo/registro.html",
                                  {'register_form': form})
