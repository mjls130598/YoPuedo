import logging
from http import HTTPStatus

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import get_template

from .utils import Utils
from .forms import RegistroForm, InicioForm, ClaveForm, RetoGeneralForm, RetoEtapasForm
from .models import Usuario

logger = logging.getLogger(__name__)
utils = Utils()


##########################################################################################

# Función de registro
def registrarse(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            logger.info("Nos redirigimos a la siguiente página")
            valuenext = request.POST.get('next')
            if valuenext:
                return HttpResponseRedirect(valuenext)
            else:
                return HttpResponseRedirect('/mis_retos/')

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

            clave_aleatoria, clave_fija = utils.guardar_usuario(utils, email,
                                                                nombre, password,
                                                                foto)
            enviar_clave(clave_aleatoria, email, "Registro en la aplicación Yo Puedo")
            enviar_clave_fija(clave_fija, email)

            return render(request, "YoPuedo/registro.html",
                          {'register_form': form,
                           'url': f'/validar_clave/registro/{email}'},
                          status=HTTPStatus.CREATED)

        else:
            logger.error("Error al validar el formulario")

    return render(request, "YoPuedo/registro.html", {'register_form': form})


##########################################################################################

# Función de envío de claves
def enviar_clave(clave, email, contexto):
    template = get_template('YoPuedo/envio_correos/envio_clave.html')
    context = {
        'titulo': "¿Eres tú?",
        'contexto': contexto,
        'clave': clave
    }
    content = template.render(context)

    utils.enviar_correo(content, email, contexto)


##########################################################################################

# Función de envío de clave fija
def enviar_clave_fija(clave, email):
    template = get_template('YoPuedo/envio_correos/envio_clave_fija.html')
    context = {
        'clave': clave
    }
    content = template.render(context)

    utils.enviar_correo(content, email, "Bienvenido a Yo Puedo")


##########################################################################################

# Función de inicio de sesión
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
            clave_aleatoria = utils.claves_aleatorias(10)
            enviar_clave(clave_aleatoria, email, "Inicio de sesión en la aplicación Yo "
                                                 "Puedo")

            user = Usuario.objects.get(email=email)
            user.update_clave(clave_aleatoria)

            return redirect(f'/validar_clave/inicio_sesion/{email}')
        else:
            logger.error("Error al validar el formulario")

    return render(request, "YoPuedo/iniciar_sesion.html", {'inicio_form': form})


##########################################################################################

# Función de validación de clave
def validar_clave(request, tipo, email):
    if request.method == 'GET':
        logger.info("Entramos en la parte GET de VALIDAR CLAVE")
        clave_form = ClaveForm(initial={'email': email, 'contador': 0})

    else:
        logger.info("Entramos en la parte POST de VALIDAR CLAVE")
        logger.info("Comprobamos si la clave introducida es la correcta")

        clave_form = ClaveForm(request.POST)

        if clave_form.is_valid():
            if tipo == 'registro' or tipo == 'inicio_sesion':
                user = Usuario.objects.get(email=email)
                if user is not None:
                    logger.info("Iniciamos sesión")
                    login(request, user,
                          backend='django.contrib.auth.backends.ModelBackend')
                    return HttpResponse(status=HTTPStatus.ACCEPTED)

        else:
            contador = int(clave_form['contador'].value())
            clave = clave_form['clave'].value()

            if contador < 2:
                logger.info(f"Intento nº {contador + 1}")
                data = {'contador': contador + 1, 'email': email, 'clave': clave}
                clave_form = ClaveForm(data)
                clave_form.is_valid()

            else:
                logger.info("Demasiados intentos. Volvemos al principio")
                if tipo == 'registro' or tipo == 'inicio_sesion':
                    logger.info("Mandamos a la página de registro")
                    if tipo == 'registro':
                        Usuario.objects.get(email=email).delete()

                return HttpResponse(status=HTTPStatus.FORBIDDEN)

    return render(request, "YoPuedo/peticion-clave.html", {'peticion_clave': clave_form})


##########################################################################################

# Función de obtención de retos
@login_required
def mis_retos(request):
    logger.info("Entramos en la parte GET de MIS RETOS")
    tipo = request.GET.get("tipo")
    if tipo == 'individuales' or tipo == 'colectivos':
        logger.info(f"Mostramos los retos {tipo}")

    elif tipo != '':
        logger.error("Tipo incorrecto")
        tipo = ""

    categoria = request.GET.get("categoria")

    if categoria in Utils.CATEGORIAS_CHOOSE:
        logger.info(f"Mostramos los retos  de la categoría {categoria}")
    else:
        logger.error("Categoría no encontrada")
        categoria = ""

    return render(request, "YoPuedo/mis_retos.html",
                  {"tipo_reto": tipo, "categoria": categoria})


@login_required
def nuevo_reto(request):
    tipo = request.GET.get("tipo")
    siguiente_paso = ""
    siguiente_etapa = ""
    num_etapas = 1
    general_form = RetoGeneralForm()
    etapa_1_form = RetoEtapasForm(prefix='1-etapa')
    etapa_2_form = RetoEtapasForm(prefix='2-etapa')
    etapa_3_form = RetoEtapasForm(prefix='3-etapa')
    etapa_4_form = RetoEtapasForm(prefix='4-etapa')
    etapa_5_form = RetoEtapasForm(prefix='5-etapa')

    if tipo == 'individuales' or tipo == 'colectivos':
        if request.method == 'GET':
            logger.info("Entramos en la parte GET de NUEVO RETO")

        else:
            logger.info("Entramos en la parte POST de NUEVO RETO")
            logger.info(f"Creamos un reto de tipo {tipo}")

            general_form = RetoGeneralForm(request.POST)
            etapa_1_form = RetoEtapasForm(data=request.POST, prefix='1-etapa')
            etapa_2_form = RetoEtapasForm(data=request.POST, prefix='2-etapa')
            etapa_3_form = RetoEtapasForm(data=request.POST, prefix='3-etapa')
            etapa_4_form = RetoEtapasForm(data=request.POST, prefix='4-etapa')
            etapa_5_form = RetoEtapasForm(data=request.POST, prefix='5-etapa')
            num_etapas = int(request.POST.get('num_etapas'))

            if 'general' in request.POST:
                logger.info("Comprobamos nuevo reto GENERAL")
                if general_form.is_valid():
                    logger.info("Válido formulario nuevo reto GENERAL")
                    siguiente_paso = 'etapas'
                    siguiente_etapa = str(num_etapas) + '-etapa'
                else:
                    logger.error("Hay errores en la pestaña GENERAL")

            if '1-etapa' in request.POST:
                logger.info("Comprobamos nuevo reto 1º ETAPA")
                etapa_1_value = request.POST.get('2-etapa')

                if etapa_1_value == 'borrar_etapa':
                    logger.info("Borramos 1º ETAPA")
                    if num_etapas == 1:
                        etapa_1_form = RetoEtapasForm(prefix='1-etapa')
                    else:
                        etapa_2_form = etapa_3_form
                        etapa_2_form.prefix = '2-etapa'
                        etapa_3_form = etapa_4_form
                        etapa_3_form.prefix = '3-etapa'
                        etapa_4_form = etapa_5_form
                        etapa_4_form.prefix = '4-etapa'
                        etapa_5_form = RetoEtapasForm(prefix='5-etapa')
                        num_etapas -= 1

                    siguiente_etapa = '1-etapa'
                    siguiente_paso = 'etapas'

                elif etapa_1_form.is_valid():
                    logger.info("Válido formulario nuevo reto 1º ETAPA")
                    if etapa_1_value == 'siguiente_etapa':
                        logger.info("Marchamos a la 2ª ETAPA")
                        siguiente_etapa = '2-etapa'
                        siguiente_paso = 'etapas'

                        if num_etapas < 2:
                            num_etapas = 2

                    elif etapa_1_value == 'siguiente_paso':
                        logger.info("Marchamos al siguiente paso")
                        siguiente_paso = 'animadores' if tipo == 'individuales' else 'participantes'

                    elif etapa_1_value == 'anterior_paso':
                        logger.info("Marchamos al paso GENERAL")
                        siguiente_paso = 'general'

                else:
                    logger.error("Hay errores en la pestaña 1º ETAPA")
                    siguiente_paso = 'etapas'
                    siguiente_etapa = '1-etapa'

            if '2-etapa' in request.POST:
                logger.info("Comprobamos nuevo reto 2º ETAPA")
                etapa_2_value = request.POST.get('2-etapa')

                if etapa_2_value == 'borrar_etapa':
                    logger.info("Borramos 2º ETAPA")
                    if num_etapas == 2:
                        siguiente_etapa = '1-etapa'
                        etapa_2_form = RetoEtapasForm(prefix='2-etapa')
                    else:
                        etapa_2_form = etapa_3_form
                        etapa_2_form.prefix = '2-etapa'
                        etapa_3_form = etapa_4_form
                        etapa_3_form.prefix = '3-etapa'
                        etapa_4_form = etapa_5_form
                        etapa_4_form.prefix = '4-etapa'
                        etapa_5_form = RetoEtapasForm(prefix='5-etapa')
                        siguiente_etapa = '2-etapa'

                    siguiente_paso = 'etapas'
                    num_etapas -= 1

                elif etapa_2_form.is_valid():
                    logger.info("Válido formulario nuevo reto 2º ETAPA")
                    if etapa_2_value == 'siguiente_etapa':
                        logger.info("Marchamos a la 3ª ETAPA")
                        siguiente_etapa = '3-etapa'
                        siguiente_paso = 'etapas'

                        if num_etapas < 3:
                            num_etapas = 3

                    elif etapa_2_value == 'anterior_etapa':
                        logger.info("Marchamos a la 1ª ETAPA")
                        siguiente_etapa = '1-etapa'
                        siguiente_paso = 'etapas'

                    elif etapa_2_value == 'siguiente_paso':
                        logger.info("Marchamos al siguiente paso")
                        siguiente_paso = 'animadores' if tipo == 'individuales' else 'participantes'

                    elif etapa_2_value == 'anterior_paso':
                        logger.info("Marchamos al paso GENERAL")
                        siguiente_paso = 'general'
                else:
                    logger.error("Hay errores en la pestaña 2º ETAPA")
                    siguiente_paso = 'etapas'
                    siguiente_etapa = '2-etapa'

            if '3-etapa' in request.POST:
                logger.info("Comprobamos nuevo reto 3º ETAPA")

                etapa_3_value = request.POST.get('3-etapa')

                if etapa_3_value == 'borrar_etapa':
                    logger.info("Borramos 3º ETAPA")
                    if num_etapas == 3:
                        siguiente_etapa = '2-etapa'
                        etapa_3_form = RetoEtapasForm(prefix='3-etapa')
                    else:
                        etapa_3_form = etapa_4_form
                        etapa_3_form.prefix = '3-etapa'
                        etapa_4_form = etapa_5_form
                        etapa_4_form.prefix = '4-etapa'
                        etapa_5_form = RetoEtapasForm(prefix='5-etapa')
                        siguiente_etapa = '3-etapa'

                    siguiente_paso = 'etapas'
                    num_etapas -= 1

                elif etapa_3_form.is_valid():
                    logger.info("Válido formulario nuevo reto 3º ETAPA")
                    etapa_3_value = request.POST.get('3-etapa')
                    if etapa_3_value == 'siguiente_etapa':
                        logger.info("Marchamos a la 4ª ETAPA")
                        siguiente_etapa = '4-etapa'
                        siguiente_paso = 'etapas'

                        if num_etapas < 4:
                            num_etapas = 4

                    elif etapa_3_value == 'anterior_etapa':
                        logger.info("Marchamos a la 2ª ETAPA")
                        siguiente_etapa = '2-etapa'
                        siguiente_paso = 'etapas'

                    elif etapa_3_value == 'siguiente_paso':
                        logger.info("Marchamos al siguiente paso")
                        siguiente_paso = 'animadores' if tipo == 'individuales' else 'participantes'

                    elif etapa_3_value == 'anterior_paso':
                        logger.info("Marchamos al paso GENERAL")
                        siguiente_paso = 'general'
                else:
                    logger.error("Hay errores en la pestaña 3º ETAPA")
                    siguiente_paso = 'etapas'
                    siguiente_etapa = '3-etapa'

            if '4-etapa' in request.POST:
                logger.info("Comprobamos nuevo reto 4º ETAPA")

                etapa_4_value = request.POST.get('4-etapa')

                if etapa_4_value == 'borrar_etapa':
                    logger.info("Borramos 4º ETAPA")
                    if num_etapas == 4:
                        siguiente_etapa = '3-etapa'
                        etapa_4_form = RetoEtapasForm(prefix='4-etapa')
                    else:
                        etapa_4_form = etapa_5_form
                        etapa_4_form.prefix = '4-etapa'
                        etapa_5_form = RetoEtapasForm(prefix='5-etapa')
                        siguiente_etapa = '4-etapa'

                    siguiente_paso = 'etapas'
                    num_etapas -= 1

                elif etapa_4_form.is_valid():
                    logger.info("Válido formulario nuevo reto 4º ETAPA")
                    if etapa_4_value == 'siguiente_etapa':
                        logger.info("Marchamos a la 5ª ETAPA")
                        siguiente_etapa = '5-etapa'
                        siguiente_paso = 'etapas'

                        if num_etapas < 5:
                            num_etapas = 5

                    elif etapa_4_value == 'anterior_etapa':
                        logger.info("Marchamos a la 3º ETAPA")
                        siguiente_etapa = '3-etapa'
                        siguiente_paso = 'etapas'

                    elif etapa_4_value == 'siguiente_paso':
                        logger.info("Marchamos al siguiente paso")
                        siguiente_paso = 'animadores' if tipo == 'individuales' else 'participantes'

                    elif etapa_4_value == 'anterior_paso':
                        logger.info("Marchamos al paso GENERAL")
                        siguiente_paso = 'general'
                else:
                    logger.error("Hay errores en la pestaña 4º ETAPA")
                    siguiente_paso = 'etapas'
                    siguiente_etapa = '4-etapa'

            if '5-etapa' in request.POST:
                logger.info("Comprobamos nuevo reto 5º ETAPA")
                etapa_5_value = request.POST.get('5-etapa')

                if etapa_5_value == 'borrar_etapa':
                    logger.info("Borramos 5º ETAPA")
                    num_etapas -= 1
                    etapa_5_form = RetoEtapasForm(prefix='5-etapa')
                    siguiente_etapa = '4-etapa'
                    siguiente_paso = 'etapas'

                elif etapa_5_form.is_valid():
                    logger.info("Válido formulario nuevo reto 5º ETAPA")
                    if etapa_5_value == 'anterior_etapa':
                        logger.info("Marchamos a la 4º ETAPA")
                        siguiente_etapa = '4-etapa'
                        siguiente_paso = 'etapas'

                    elif etapa_5_value == 'siguiente_paso':
                        logger.info("Marchamos al paso siguiente")
                        siguiente_paso = 'animadores' if tipo == 'individuales' else 'participantes'

                    elif etapa_5_value == 'anterior_paso':
                        logger.info("Marchamos al paso GENERAL")
                        siguiente_paso = 'general'

                else:
                    logger.error("Hay errores en la pestaña 5º ETAPA")
                    siguiente_paso = 'etapas'
                    siguiente_etapa = '5-etapa'

    elif tipo != '':
        logger.error("Tipo incorrecto")
        tipo = ""

    return render(request, "YoPuedo/nuevo_reto.html",
                  {"tipo_reto": tipo, "general_form": general_form,
                   "etapa_1_form": etapa_1_form, "etapa_2_form": etapa_2_form,
                   "etapa_3_form": etapa_3_form, "etapa_4_form": etapa_4_form,
                   "etapa_5_form": etapa_5_form, "siguiente": siguiente_paso,
                   "siguiente_etapa": siguiente_etapa, "num_etapas": num_etapas})
