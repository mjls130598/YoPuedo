import logging
import os
from http import HTTPStatus
from itertools import chain

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template

from .utils import Utils
from .forms import RegistroForm, InicioForm, ClaveForm, RetoGeneralForm, RetoEtapaForm, \
    AmigosForm, EtapasFormSet
from .models import Usuario, Amistad, Reto, Etapa, Animador, Participante, Animo, Prueba, \
    Calificacion

from django.forms import formset_factory

from TFM.settings import BASE_DIR

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

# Función de obtención de retos (página con los estados y las categorías)
@login_required
def mis_retos(request):
    logger.info("Entramos en la parte GET de MIS RETOS")
    tipo = request.GET.get("tipo")
    categoria = request.GET.get("categoria")
    propuestos = []

    if categoria in Utils.categorias:
        logger.info(f"Mostramos los retos  de la categoría {categoria}")
    else:
        logger.error("Categoría no encontrada")
        categoria = ""

    if tipo == 'individuales' or tipo == 'colectivos':
        logger.info(f"Mostramos los retos propuestos de {tipo}")

        logger.info("Buscamos los retos según la categoría dada y el tipo de reto, "
                    + "separada en según el estado")

        if not categoria:
            propuestos = \
                Reto.objects.filter(estado='Propuesto',
                                    participante__usuario=request.user). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt__lte=1) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(estado='Propuesto',
                                        participante__usuario=request.user). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=1)

        else:
            propuestos = \
                Reto.objects.filter(estado='Propuesto',
                                    participante__usuario=request.user,
                                    categoria=categoria). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt__lte=1) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(estado='Propuesto',
                                        participante__usuario=request.user,
                                        categoria=categoria). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=1)

        logger.info("Paginamos los retos")
        paginator_propuestos = Paginator(propuestos, 3)

        logger.info("Obtenemos los retos de la página indicada para ese estado")
        propuestos = paginator_propuestos.get_page(1)

    elif tipo != '':
        logger.error("Tipo incorrecto")
        tipo = ""

    return render(request, "YoPuedo/mis_retos.html",
                  {"tipo_reto": tipo, "categoria": categoria, "propuestos": propuestos,
                   "estado": "propuestos"})


##########################################################################################

# Función de obtención de retos según el tipo, la categoría y el estado, además de la
# página de retos que se quiera visualizar
def get_retos(request):
    logger.info("Entramos en la parte GET de RETOS")
    tipo = request.GET.get("tipo")
    categoria = request.GET.get("categoria")
    pagina = request.GET.get("page")
    estado = request.GET.get("estado")

    retos = []

    logger.info(f"Mostramos los retos {tipo} de {categoria} y en estado {estado}")

    logger.info("Buscamos los retos según la categoría dada y el tipo de reto, "
                + "separada en según el estado")

    if not categoria:
        if estado == "propuestos":
            retos = \
                Reto.objects.filter(estado='Propuesto',
                                    participante__usuario=request.user). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt__lte=1) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(estado='Propuesto',
                                        participante__usuario=request.user). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=1)

        elif estado == "proceso":
            retos = \
                Reto.objects.filter(estado='En proceso',
                                    participante__usuario=request.user). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt__lte=1) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(estado='En proceso',
                                        participante__usuario=request.user). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=1)

        elif estado == "finalizados":
            retos = \
                Reto.objects.filter(estado='Finalizado',
                                    participante__usuario=request.user). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt__lte=1) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(estado='Finalizado',
                                        participante__usuario=request.user). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=1)

        elif estado == "animando":
            retos = \
                Reto.objects.filter(animador__usuario=request.user). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt__lte=1) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(animador__usuario=request.user). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=1)

    else:
        if estado == "propuestos":
            retos = \
                Reto.objects.filter(estado='Propuesto',
                                    participante__usuario=request.user,
                                    categoria=categoria). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt__lte=1) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(estado='Propuesto',
                                        participante__usuario=request.user,
                                        categoria=categoria). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=1)

        elif estado == "proceso":
            retos = \
                Reto.objects.filter(estado='En proceso',
                                    participante__usuario=request.user,
                                    categoria=categoria). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt__lte=1) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(estado='En proceso',
                                        participante__usuario=request.user,
                                        categoria=categoria). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=1)

        elif estado == "finalizados":
            retos = \
                Reto.objects.filter(estado='Finalizado',
                                    participante__usuario=request.user,
                                    categoria=categoria). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt__lte=1) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(estado='Finalizado',
                                        participante__usuario=request.user,
                                        categoria=categoria). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=1)

        elif estado == "animando":
            retos = \
                Reto.objects.filter(animador__usuario=request.user,
                                    categoria=categoria). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt__lte=1) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(animador__usuario=request.user,
                                        categoria=categoria). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=1)

    logger.info("Paginamos cada uno de los estados del reto")
    paginator = Paginator(retos, 3)

    logger.info("Obtenemos los retos de la página indicada para ese estado")

    try:
        retos = paginator.get_page(pagina)
    except PageNotAnInteger:
        retos = paginator.get_page(1)
    except EmptyPage:
        retos = paginator.get_page(1)

    return render(request, "YoPuedo/elementos/reto.html",
                  {"estado": estado, "retos": retos})


##########################################################################################

# Función de creación de retos
@login_required
def nuevo_reto(request):
    tipo = request.GET.get("tipo")
    max_etapas = 5
    general_form = RetoGeneralForm()
    etapas_form_model = formset_factory(RetoEtapaForm, formset=EtapasFormSet,
                                        max_num=max_etapas)
    etapas_form = etapas_form_model()
    errores = False
    animadores = []
    participantes = []
    etapas_validas = True

    if tipo == 'individual' or tipo == 'colectivo':
        if request.method == 'GET':
            logger.info("Entramos en la parte GET de NUEVO RETO")

        else:
            logger.info("Entramos en la parte POST de NUEVO RETO")
            logger.info(f"Creamos un reto de tipo {tipo}")

            # Primero obtenemos los animadores
            logger.info("Obtenemos animadores")
            animadores_email = request.POST.getlist('animador')

            # Segundo obtenemos los participantes
            logger.info("Obtenemos participantes")
            participantes_email = request.POST.getlist('participante')

            # Después obtenemos la parte general y las etapas del reto
            general_form = RetoGeneralForm(request.POST, request.FILES)
            etapas_form = etapas_form_model(request.POST, request.FILES)

            etapas_validas = etapas_form.is_valid()
            # Comprobamos si la parte principal es correcto
            if general_form.is_valid() and etapas_validas:
                logger.info("Guardamos formulario NUEVO RETO")

                # Guardamos ID del reto
                id_reto = Utils.crear_id_reto()
                logger.info(f"NUEVO RETO: {id_reto}")

                # Obtenemos datos de la pestaña GENERAL
                titulo = general_form.cleaned_data['titulo'].value()
                logger.info(f'TÍTULO: {titulo}')

                objetivo_texto = general_form.cleaned_data['objetivo_texto'].value()
                objetivo_imagen = request.FILES["objetivo_imagen"] \
                    if 'objetivo_imagen' in request.FILES else None
                objetivo_audio = request.FILES["objetivo_audio"] \
                    if 'objetivo_audio' in request.FILES else None
                objetivo_video = request.FILES["objetivo_video"] \
                    if 'objetivo_video' in request.FILES else None

                objetivo_multimedia = objetivo_imagen if objetivo_imagen else (
                    objetivo_audio if objetivo_audio else objetivo_video)

                if objetivo_multimedia:
                    fichero, extension = os.path.splitext(objetivo_multimedia.name)
                    directorio = os.path.join(BASE_DIR, "media", "YoPuedo", id_reto)
                    localizacion = os.path.join(directorio, 'OBJETIVO' + extension)
                    objetivo = os.path.join("/media", "YoPuedo", id_reto,
                                            'OBJETIVO' + extension)
                    try:
                        Utils.handle_uploaded_file(objetivo_multimedia, localizacion,
                                                   directorio)
                    except:
                        logger.error("Error al subir el objetivo")
                else:
                    objetivo = objetivo_texto

                logger.info(f"OBJETIVO: {objetivo}")

                recompensa_texto = general_form.cleaned_data['recompensa_texto'].value()
                recompensa_imagen = request.FILES["recompensa_imagen"] \
                    if 'recompensa_imagen' in request.FILES else None
                recompensa_audio = request.FILES["recompensa_audio"] \
                    if 'recompensa_audio' in request.FILES else None
                recompensa_video = request.FILES["recompensa_video"] \
                    if 'recompensa_video' in request.FILES else None

                recompensa_multimedia = recompensa_imagen if recompensa_imagen else (
                    recompensa_audio if recompensa_audio else recompensa_video)

                if recompensa_multimedia:
                    fichero, extension = os.path.splitext(recompensa_multimedia.name)
                    directorio = os.path.join(BASE_DIR, "media", "YoPuedo", id_reto)
                    localizacion = os.path.join(directorio, 'RECOMPENSA' + extension)
                    recompensa = os.path.join("/media", "YoPuedo", id_reto,
                                              'RECOMPENSA' + extension)
                    try:
                        Utils.handle_uploaded_file(recompensa_multimedia, localizacion,
                                                   directorio)
                    except:
                        logger.error("Error al subir el objetivo")
                else:
                    recompensa = recompensa_texto

                logger.info(f"RECOMPENSA: {recompensa}")

                categoria = general_form.cleaned_data['categoria'].value()
                logger.info(f"CATEGORIA: {categoria}")

                # Creamos reto
                reto = Reto(id_reto=id_reto, titulo=titulo,
                            objetivo=objetivo, recompensa=recompensa,
                            categoria=categoria, coordinador=request.user)

                reto.save()

                # Guardamos datos de las pestañas de ETAPAS
                logger.info("Creación de ETAPAS")
                for index, etapa_form in enumerate(etapas_form):
                    id_etapa = Utils.crear_id_etapa()
                    logger.info(f"NUEVA ETAPA {id_etapa}")
                    objetivo_texto = etapa_form.cleaned_data['objetivo_texto'].value()
                    objetivo_imagen = request.FILES[f"form-{index}-objetivo_imagen"] \
                        if f"form-{index}-objetivo_imagen" in request.FILES else None
                    objetivo_audio = request.FILES[f"form-{index}-objetivo_audio"] \
                        if f"form-{index}-objetivo_audio" in request.FILES else None
                    objetivo_video = request.FILES[f"form-{index}-objetivo_video"] \
                        if f"form-{index}-objetivo_video" in request.FILES else None

                    objetivo_multimedia = objetivo_imagen if objetivo_imagen else (
                        objetivo_audio if objetivo_audio else objetivo_video)

                    if objetivo_multimedia:
                        fichero, extension = os.path.splitext(objetivo_multimedia.name)
                        directorio = os.path.join(BASE_DIR, "media", "YoPuedo", id_reto,
                                                  id_etapa)
                        localizacion = os.path.join(directorio, 'OBJETIVO' + extension)
                        objetivo = os.path.join("/media", "YoPuedo", id_reto, id_etapa,
                                                'OBJETIVO' + extension)
                        try:
                            Utils.handle_uploaded_file(objetivo_multimedia, localizacion,
                                                       directorio)
                        except:
                            logger.error("Error al subir el objetivo")
                    else:
                        objetivo = objetivo_texto

                    logger.info(f"OBJETIVO: {objetivo}")

                    Etapa(id_etapa=id_etapa, reto=reto, objetivo=objetivo).save()

                logger.info("Inserción de ANIMADORES")
                # Guardamos a los animadores del reto
                for animador_email in animadores_email:
                    logger.info(f"ANIMADOR: {animador_email}")
                    usuario = Usuario.objects.get(email=animador_email)
                    superanimador = request.POST.get(
                        f'superanimador-{animador_email}') == "true"
                    animador = Animador()
                    animador.save()
                    animador.reto.add(reto)
                    animador.usuario.add(usuario)
                    animador.superanimador = superanimador
                    animador.save()

                logger.info("Inserción de PARTICIPANTES")
                # Guardamos a los participantes del reto
                for participante_email in participantes_email:
                    logger.info(f"PARTICIPANTE: {participante_email}")
                    usuario = Usuario.objects.get(email=participante_email)
                    participante = Participante()
                    participante.save()
                    participante.reto.add(reto)
                    participante.usuario.add(usuario)
                    participante.save()

                # Añadimos al usuario como participante también
                logger.info("Inserción del COORDINADOR como PARTICIPANTE")
                participante = Participante()
                participante.save()
                participante.reto.add(reto)
                participante.usuario.add(request.user)
                participante.save()

                # Redireccionamos a la visualización del reto
                return redirect(f'/mis_retos/{id_reto}')

            else:
                logger.error("Error al validar formulario NUEVO RETO")
                errores = True

                # De cada animador, obtenemos su usuario y si es superanimador
                for animador_email in animadores_email:
                    logger.info(f"Animador {animador_email}")
                    usuario = Usuario.objects.filter(email=animador_email) \
                        .values('email', 'foto_perfil', 'nombre')[0]
                    superanimador = request.POST.get(f'superanimador-{animador_email}')
                    animadores.append(
                        {'usuario': usuario, 'superanimador': superanimador})

                # De cada participante, obtenemos su usuario
                for participante_email in participantes_email:
                    logger.info(f"Participante {participante_email}")
                    usuario = Usuario.objects.filter(email=participante_email) \
                        .values('email', 'foto_perfil', 'nombre')[0]
                    logger.info(f"Obtenemos datos usuario: {usuario.email}, "
                                f"{usuario.foto_perfil}, {usuario.nombre}")
                    participantes.append({'usuario': usuario})

    elif tipo != '':
        logger.error("Tipo incorrecto")
        tipo = ""

    return render(request, "YoPuedo/nuevo_reto.html",
                  {"tipo_reto": tipo, "general_form": general_form,
                   "etapas_form": etapas_form, "errores": errores,
                   "max_etapas": max_etapas, "animadores": animadores,
                   "participantes": participantes, "error_etapas": not etapas_validas})


##########################################################################################

# Función de obtención de amigos
@login_required
def get_amigos(request):
    relacion = request.GET.get('relacion')
    formulario = AmigosForm(request.GET)
    consulta = formulario.data['consulta'] if 'consulta' in formulario.data else ""
    pagina = request.GET.get('page')

    amigos_amigo = Amistad.objects.filter(Q(amigo=request.user)) \
        .annotate(email=F('otro_amigo__email'),
                  foto_perfil=F('otro_amigo__foto_perfil'),
                  nombre=F('otro_amigo__nombre')) \
        .values('email', 'foto_perfil', 'nombre') if not consulta else \
        Amistad.objects.filter(Q(amigo=request.user),
                               Q(otro_amigo__email__contains=consulta) |
                               Q(otro_amigo__nombre__contains=consulta)) \
            .annotate(email=F('otro_amigo__email'),
                      foto_perfil=F('otro_amigo__foto_perfil'),
                      nombre=F('otro_amigo__nombre')) \
            .values('email', 'foto_perfil', 'nombre')

    amigos_otro = Amistad.objects.filter(Q(otro_amigo=request.user)) \
        .annotate(email=F('amigo__email'),
                  foto_perfil=F('amigo__foto_perfil'),
                  nombre=F('amigo__nombre')) \
        .values('email', 'foto_perfil', 'nombre') if not consulta else \
        Amistad.objects.filter(Q(otro_amigo=request.user),
                               Q(amigo__email__contains=consulta) |
                               Q(amigo__nombre__contains=consulta)) \
            .annotate(email=F('amigo__email'),
                      foto_perfil=F('amigo__foto_perfil'),
                      nombre=F('amigo__nombre')) \
            .values('email', 'foto_perfil', 'nombre')

    amigos = list(chain(amigos_amigo, amigos_otro))

    logger.info("Paginamos cada uno de los estados del reto")
    paginator = Paginator(amigos, 3)

    logger.info("Obtenemos los retos de la página indicada para ese estado")

    try:
        amigos = paginator.get_page(pagina)
    except PageNotAnInteger:
        amigos = paginator.get_page(1)
    except EmptyPage:
        amigos = paginator.get_page(1)

    return render(request, "YoPuedo/elementos/modal-amigos.html",
                  {"relacion": relacion, "amigos": amigos, "form_consulta": formulario})


##########################################################################################

# Función de obtención de información de un reto
@login_required
def get_reto(request, id_reto):
    logger.info(f"Obtenemos información de {id_reto}")
    reto = get_object_or_404(Reto, id_reto=id_reto)

    logger.info(f"Recogemos las etapas del reto {id_reto}")
    etapas = Etapa.objects.filter(reto=reto)

    logger.info(f"Miramos los animadores del reto {id_reto}")
    animadores = Animador.objects.filter(reto__id_reto=id_reto). \
        exclude(usuario__email=request.user.email)

    logger.info(f"Devolvemos los participantes del reto {id_reto}")
    participantes = Participante.objects.filter(reto__id_reto=id_reto). \
        exclude(usuario__email=request.user.email)

    return render(request, 'YoPuedo/reto.html',
                  {'reto': reto, 'etapas': etapas, 'animadores': animadores,
                   'participantes': participantes})


##########################################################################################

# Función para iniciar el reto
@login_required
def iniciar_reto(request, id_reto):
    logger.info(f"Iniciamos el reto {id_reto}")
    reto = Reto.objects.get(id_reto=id_reto)
    reto.estado = "En proceso"
    reto.save()

    logger.info("Iniciamos la primera etapa del reto")
    etapa = Etapa.objects.filter(reto__id_reto=id_reto)[0]
    etapa.estado = "En proceso"
    etapa.save()

    logger.info(f"Redirigimos a la página del reto")
    return redirect(f"/reto/{id_reto}")


##########################################################################################

# Función para editar el reto
@login_required
def editar_reto(request, id_reto):
    max_etapas = 5
    general_form = RetoGeneralForm()
    etapas_form_model = formset_factory(RetoEtapaForm, formset=EtapasFormSet,
                                        max_num=max_etapas)
    etapas_form = etapas_form_model()
    errores = False
    animadores = []
    participantes = []
    etapas_validas = True

    if request.method == 'GET':
        logger.info("Entramos en la parte GET de EDITAR RETO")

    else:
        logger.info("Entramos en la parte POST de EDITAR RETO")
        logger.info(f"Modificamos el reto {id_reto}")

    return render(request, "YoPuedo/nuevo_reto.html",
                  {"general_form": general_form,
                   "etapas_form": etapas_form, "errores": errores,
                   "max_etapas": max_etapas, "animadores": animadores,
                   "participantes": participantes, "error_etapas": not etapas_validas})


##########################################################################################

# Función para eliminar el reto
@login_required
def eliminar_reto(request, id_reto):
    logger.info("Eliminamos los ánimos del reto")
    Animo.objects.filter(etapa__reto__id_reto=id_reto).delete()

    logger.info("Eliminamos las pruebas del reto")
    Prueba.objects.filter(etapa__reto__id_reto=id_reto).delete()

    logger.info("Eliminamos las calificaciones del reto")
    Calificacion.objects.filter(etapa__reto__id_reto=id_reto).delete()

    logger.info("Eliminamos las etapas del reto")
    Etapa.objects.filter(reto__id_reto=id_reto).delete()

    logger.info("Eliminamos los animadores del reto")
    Animador.objects.filter(reto__id_reto=id_reto).delete()

    logger.info("Eliminamos los participantes del reto")
    Participante.objects.filter(reto__id_reto=id_reto).delete()

    logger.info(f"Eliminamos el reto {id_reto}")
    Reto.objects.get(id_reto=id_reto).delete()

    logger.info(f"Redirigimos a la página de mis retos")
    return redirect(f"/mis_retos/")


##########################################################################################

# Función para mostrar el error 404
def page_not_found(request):
    render(request, '404.html', status=404)
