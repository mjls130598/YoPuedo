import logging
import os
from http import HTTPStatus
from itertools import chain

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template

from .utils import Utils
from .forms import RegistroForm, InicioForm, ClaveForm, RetoGeneralForm, RetoEtapaForm, \
    AmigosForm, EtapasFormSet
from .models import Usuario, Amistad, Reto, Etapa, Animador, Participante

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
                                    coordinador=request.user). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt=0) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(Q(estado='Propuesto'),
                                        Q(coordinador=request.user) |
                                        Q(participante__usuario=request.user)). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=0)

        else:
            propuestos = \
                Reto.objects.filter(estado='Propuesto',
                                    coordinador=request.user,
                                    categoria=categoria). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt=0) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(Q(estado='Propuesto'),
                                        Q(coordinador=request.user) |
                                        Q(participante__usuario=request.user),
                                        Q(categoria=categoria)). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=0)

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
                                    coordinador=request.user). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt=0) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(Q(estado='Propuesto'),
                                        Q(coordinador=request.user) |
                                        Q(participante__usuario=request.user)). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=0)

        elif estado == "proceso":
            retos = \
                Reto.objects.filter(estado='En proceso',
                                    coordinador=request.user). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt=0) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(Q(estado='En proceso'),
                                        Q(coordinador=request.user) |
                                        Q(participante__usuario=request.user)). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=0)

        elif estado == "finalizados":
            retos = \
                Reto.objects.filter(estado='Finalizado',
                                    coordinador=request.user). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt=0) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(Q(estado='Finalizado'),
                                        Q(coordinador=request.user) |
                                        Q(participante__usuario=request.user)). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=0)

        elif estado == "animando":
            retos = \
                Reto.objects.filter(animador__usuario=request.user). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt=0) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(animador__usuario=request.user). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=0)

    else:
        if estado == "propuestos":
            retos = \
                Reto.objects.filter(estado='Propuesto',
                                    coordinador=request.user,
                                    categoria=categoria). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt=0) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(Q(estado='Propuesto'),
                                        Q(coordinador=request.user) |
                                        Q(participante__usuario=request.user),
                                        Q(categoria=categoria)). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=0)

        elif estado == "proceso":
            retos = \
                Reto.objects.filter(estado='En proceso',
                                    coordinador=request.user,
                                    categoria=categoria). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt=0) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(Q(estado='En proceso'),
                                        Q(coordinador=request.user) |
                                        Q(participante__usuario=request.user),
                                        Q(categoria=categoria)). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=0)

        elif estado == "finalizados":
            retos = \
                Reto.objects.filter(estado='Finalizado',
                                    coordinador=request.user,
                                    categoria=categoria). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt=0) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(Q(estado='Finalizado'),
                                        Q(coordinador=request.user) |
                                        Q(participante__usuario=request.user),
                                        Q(categoria=categoria)). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=0)

        elif estado == "animando":
            retos = \
                Reto.objects.filter(animador__usuario=request.user,
                                    categoria=categoria). \
                    annotate(cnt=Count('participante__usuario')).filter(cnt=0) \
                    if tipo == 'individuales' else \
                    Reto.objects.filter(animador__usuario=request.user,
                                        categoria=categoria). \
                        annotate(cnt=Count('participante__usuario')).filter(cnt__gt=0)

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

                # Redireccionamos a la visualización del reto
                return redirect(f'/reto/{id_reto}')

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

    logger.info("Paginamos los amigos de esa persona")
    paginator = Paginator(amigos, 3)

    logger.info("Obtenemos los amigos de la página indicada para ese estado")

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
    etapas = reto.etapa_set.all()

    logger.info(f"Miramos los animadores del reto {id_reto}")
    animadores = reto.animador_set.all().exclude(usuario=request.user)

    logger.info("Modificamos la información obtenida de los animadores para mandarla a " +
                "frontend")
    animadores_finales = []

    for animador in animadores:
        animadores_finales.append({
            'usuario': animador.usuario.first(),
            'superanimador': animador.superanimador})

    logger.info(f"Devolvemos los participantes del reto {id_reto}")
    participantes = reto.participante_set.all().exclude(usuario=request.user)

    logger.info("Modificamos la información obtenida de los participantes para mandarla " +
                "a frontend")
    participantes_finales = []

    for participante in participantes:
        participantes_finales.append(participante.usuario.first())

    anima = Animador.objects.filter(reto=reto,
                                    usuario=request.user).exists()

    return render(request, 'YoPuedo/reto.html',
                  {'reto': reto, 'etapas': etapas, 'animadores': animadores_finales,
                   'participantes': participantes_finales, 'anima': anima})


##########################################################################################

# Función para iniciar el reto
@login_required
def iniciar_reto(request, id_reto):
    logger.info(f"Iniciamos el reto {id_reto}")
    reto = get_object_or_404(Reto, id_reto=id_reto)
    reto.estado = "En proceso"
    reto.save()

    logger.info("Iniciamos la primera etapa del reto")
    etapa = reto.etapa_set.first()
    etapa.estado = "En proceso"
    etapa.save()

    logger.info(f"Redirigimos a la página del reto")
    return redirect(f"/reto/{id_reto}")


##########################################################################################

# Función para editar el reto
@login_required
def editar_reto(request, id_reto):
    logger.info("Comprobamos que existe el reto")
    reto = get_object_or_404(Reto, id_reto=id_reto)

    logger.info("Recogemos el resto de información de un reto")
    animadores_reto = reto.animador_set.all()
    animadores = []

    for animador in animadores_reto:
        animadores.append({
            'usuario': animador.usuario.first(),
            'superanimador': animador.superanimador})

    participantes_reto = reto.participante_set.all()
    participantes = []
    for participante in participantes_reto:
        participantes.append(participante.usuario.first())

    max_etapas = 5
    errores = False
    etapas_validas = True
    etapas_form_model = formset_factory(RetoEtapaForm, formset=EtapasFormSet,
                                        max_num=max_etapas)

    if request.method == 'GET':
        logger.info("Entramos en la parte GET de EDITAR RETO")

        etapas = reto.etapa_set.all()
        files = {}
        data = {'titulo': reto.titulo}

        logger.info("Recogemos el tipo de objetivo del reto guardado")
        if "/media/" in reto.objetivo:
            if "jpg" in reto.objetivo or "jpeg" in reto.objetivo or "png" in \
                    reto.objetivo or "svg" in reto.objetivo or "gif" in \
                    reto.objetivo:
                objetivo_imagen = reto.objetivo
                objetivo_imagen = open(objetivo_imagen, 'rb')
                files['objetivo_imagen'] = SimpleUploadedFile(objetivo_imagen.name,
                                                              objetivo_imagen.read())
            elif "mp3" in reto.objetivo or "acc" in reto.objetivo or "ogg" in \
                    reto.objetivo or "wma" in reto.objetivo:
                objetivo_audio = reto.objetivo
                objetivo_audio = open(objetivo_audio, 'rb')
                files['objetivo_audio'] = SimpleUploadedFile(objetivo_audio.name,
                                                             objetivo_audio.read())
            elif "mp4" in reto.objetivo or "ogg" in reto.objetivo:
                objetivo_video = reto.objetivo
                objetivo_video = open(objetivo_video, 'rb')
                files['objetivo_video'] = SimpleUploadedFile(objetivo_video.name,
                                                             objetivo_video.read())
        else:
            data['objetivo_texto'] = reto.objetivo

        logger.info("Recogemos el tipo de recompensa del reto guardado")
        if "/media/" in reto.recompensa:
            if "jpg" in reto.recompensa or "jpeg" in reto.recompensa or "png" in \
                    reto.recompensa or "svg" in reto.recompensa or "gif" in \
                    reto.recompensa:
                recompensa_imagen = reto.recompensa
                recompensa_imagen = open(recompensa_imagen, 'rb')
                files['recompensa_imagen'] = SimpleUploadedFile(recompensa_imagen.name,
                                                                recompensa_imagen.read())
            elif "mp3" in reto.recompensa or "acc" in reto.recompensa or "ogg" in \
                    reto.recompensa or "wma" in reto.recompensa:
                recompensa_audio = reto.recompensa
                recompensa_audio = open(recompensa_audio, 'rb')
                files['recompensa_audio'] = SimpleUploadedFile(recompensa_audio.name,
                                                               recompensa_audio.read())
            elif "mp4" in reto.recompensa or "ogg" in reto.recompensa:
                recompensa_video = reto.recompensa
                recompensa_video = open(recompensa_video, 'rb')
                files['recompensa_video'] = SimpleUploadedFile(recompensa_video.name,
                                                               recompensa_video.read())
        else:
            data['recompensa_texto'] = reto.recompensa

        logger.info("Guardamos los datos del reto recogidos y lo mandamos a su " +
                    "formulario")
        general_form = RetoGeneralForm(data=data, files=files)

        logger.info("Recogemos la información de cada una de las etapas")
        data = {
            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': len(etapas),
            'form-MAX_NUM_FORM': '5',
        }
        files = {}

        for index, etapa in enumerate(etapas):
            logger.info("Recogemos el tipo de objetivo de la etapa guardado")
            data[f'form-{index}-id_etapa'] = etapa.id_etapa
            if "/media/" in etapa.objetivo:
                if "jpg" in etapa.objetivo or "jpeg" in etapa.objetivo or "png" in \
                        etapa.objetivo or "svg" in etapa.objetivo or "gif" in \
                        etapa.objetivo:
                    objetivo_imagen = etapa.objetivo
                    objetivo_imagen = open(objetivo_imagen, 'rb')
                    files[f'form-{index}-objetivo_imagen'] = SimpleUploadedFile(
                        objetivo_imagen.name,
                        objetivo_imagen.read())
                elif "mp3" in etapa.objetivo or "acc" in etapa.objetivo or "ogg" in \
                        etapa.objetivo or "wma" in etapa.objetivo:
                    objetivo_audio = etapa.objetivo
                    objetivo_audio = open(objetivo_audio, 'rb')
                    files[f'form-{index}-objetivo_audio'] = SimpleUploadedFile(
                        objetivo_audio.name,
                        objetivo_audio.read())
                elif "mp4" in etapa.objetivo or "ogg" in etapa.objetivo:
                    objetivo_video = etapa.objetivo
                    objetivo_video = open(objetivo_video, 'rb')
                    files[f'form-{index}-objetivo_video'] = SimpleUploadedFile(
                        objetivo_video.name,
                        objetivo_video.read())
            else:
                data[f'form-{index}-objetivo_texto'] = etapa.objetivo

        etapas_form = etapas_form_model(data, files)

    else:
        logger.info("Entramos en la parte POST de EDITAR RETO")
        logger.info(f"Modificamos el reto {id_reto}")

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
            logger.info(f"Guardamos formulario EDITAR RETO de {id_reto}")
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
                    if "/media/" in reto.objetivo:
                        Utils.eliminarArchivo(BASE_DIR + reto.objetivo)

                    Utils.handle_uploaded_file(objetivo_multimedia, localizacion,
                                               directorio)
                except:
                    logger.error("Error al subir el objetivo")
            else:
                objetivo = objetivo_texto

            if objetivo != reto.objetivo and "/media/" in reto.objetivo:
                logger.info("Borramos el antiguo objetivo del reto")
                Utils.eliminarArchivo(BASE_DIR + reto.objetivo)

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
                if recompensa_multimedia.name != reto.recompensa:
                    fichero, extension = os.path.splitext(recompensa_multimedia.name)
                    directorio = os.path.join(BASE_DIR, "media", "YoPuedo", id_reto)
                    localizacion = os.path.join(directorio, 'RECOMPENSA' + extension)
                    recompensa = os.path.join("/media", "YoPuedo", id_reto,
                                              'RECOMPENSA' + extension)
                    try:
                        Utils.handle_uploaded_file(recompensa_multimedia, localizacion,
                                                   directorio)
                    except:
                        logger.error("Error al subir la recompensa")
            else:
                recompensa = recompensa_texto

            if recompensa != reto.recompensa and "/media/" in reto.recompensa:
                logger.info("Borramos la antigua recompensa del reto")
                Utils.eliminarArchivo(BASE_DIR + reto.recompensa)

            logger.info(f"RECOMPENSA: {recompensa}")

            categoria = general_form.cleaned_data['categoria'].value()
            logger.info(f"CATEGORIA: {categoria}")

            # Guardamos reto
            reto.titulo = titulo
            reto.objetivo = objetivo
            reto.recompensa = recompensa
            reto.categoria = categoria
            reto.save()

            etapas = Etapa.objects.filter(reto=reto).values("id_etapa")
            etapas_ids = []
            logger.info("Recogemos las etapas ")
            for etapa in etapas:
                etapas_ids.append(etapa['id_etapa'])

            # Guardamos datos de las pestañas de ETAPAS
            logger.info("Modificación de ETAPAS")
            for index, etapa_form in enumerate(etapas_form):
                id_etapa = etapa_form.cleaned_data['id_etapa'].value()
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

                if id_etapa == "":
                    id_etapa = Utils.crear_id_etapa()
                    logger.info(f"NUEVA ETAPA {id_etapa}")

                    Etapa(id_etapa=id_etapa, reto=reto, objetivo=objetivo).save()
                else:
                    etapas_ids.remove(id_etapa)
                    etapa = Etapa.objects.get(id_etapa=id_etapa)
                    if objetivo != etapa.objetivo and "/media/" in etapa.objetivo:
                        logger.info(
                            f"Borramos el antiguo objetivo de la etapa {id_etapa}")
                        Utils.eliminarArchivo(BASE_DIR + reto.objetivo)
                    etapa.objetivo = objetivo
                    etapa.save()

            logger.info("Borramos en la BD las etapas del reto eliminadas")
            for etapa_id in etapas_ids:
                logger.info(f"Eliminamos la etapa {etapa_id}")
                reto.etapa_set.get(id_etapa=etapa_id).delete()

            logger.info("Obtenemos los animadores anteriores")
            animadores = reto.animador_set.all().values("usuario__email")
            animadores_antiguos_emails = []
            for animador in animadores:
                animadores_antiguos_emails.append(animador['usuario__email'])

            logger.info("Inserción de ANIMADORES")
            # Guardamos a los animadores del reto
            for animador_email in animadores_email:
                logger.info(f"ANIMADOR: {animador_email}")
                superanimador = request.POST.get(
                    f'superanimador-{animador_email}') == "true"
                if not animador_email in animadores_antiguos_emails:
                    usuario = Usuario.objects.get(email=animador_email)
                    animador = Animador()
                    animador.save()
                    animador.reto.add(reto)
                    animador.usuario.add(usuario)
                else:
                    animadores_antiguos_emails.remove(animador_email)
                    animador = reto.animador_set.get(usuario__email=animador_email)
                    animador.superanimador = superanimador
                    animador.save()

            logger.info("Borramos el resto de animadores")
            for animador_email in animadores_antiguos_emails:
                logger.info(f"Eliminamos el animador {animador_email}")
                reto.animador_set.get(usuario__email=animador_email).delete()

            logger.info("Obtenemos los participantes anteriores")
            participantes = reto.participante_set.all().values("usuario__email")
            participantes_antiguos_email = []
            for participante in participantes:
                participantes_antiguos_email.append(participante['usuario__email'])

            logger.info("Inserción de PARTICIPANTES")
            # Guardamos a los participantes del reto
            for participante_email in participantes_email:
                logger.info(f"PARTICIPANTE: {participante_email}")

                if not participante_email in participantes_antiguos_email:
                    usuario = Usuario.objects.get(email=participante_email)
                    participante = Participante()
                    participante.save()
                    participante.reto.add(reto)
                    participante.usuario.add(usuario)
                    participante.save()

                else:
                    participantes_antiguos_email.remove(participante_email)

            logger.info("Borramos el resto de participantes")
            for participante_email in participantes_antiguos_email:
                logger.info(f"Eliminamos el animador {participante_email}")
                reto.participante_set.get(usuario__email=participante_email).delete()

            # Redireccionamos a la visualización del reto
            return redirect(f'/reto/{id_reto}')

        else:
            logger.error(f"Error al validar formulario EDITAR RETO {id_reto}")
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

    return render(request, "YoPuedo/nuevo_reto.html",
                  {"general_form": general_form,
                   "etapas_form": etapas_form, "errores": errores,
                   "max_etapas": max_etapas, "animadores": animadores,
                   "participantes": participantes, "error_etapas": not etapas_validas})


##########################################################################################

# Función para eliminar el reto
@login_required
def eliminar_reto(request, id_reto):
    logger.info("Comprobamos que existe el reto")
    reto = get_object_or_404(Reto, id_reto=id_reto)

    logger.info(f"Eliminamos el reto {id_reto}")
    reto.delete()

    logger.info(f"Redirigimos a la página de mis retos")
    return redirect(f"/mis_retos/")


##########################################################################################

# Función para cambiar el coordinador del reto
@login_required
def coordinador_reto(request, id_reto):
    logger.info("Comprobamos que existe el reto")
    reto = get_object_or_404(Reto, id_reto=id_reto)

    if request.method == 'POST':
        coordinador = request.POST.get('coordinador')

        if coordinador != "":
            logger.info("Añadimos actual coordinador como participante del reto")
            reto.participante_set.add(reto.coordinador)

            logger.info(f"Cambiamos el coordinador por {coordinador}")
            reto.coordinador = Usuario.objects.get(email=coordinador)
            reto.save()

            logger.info(f"Redirigimos con un status {HTTPStatus.ACCEPTED}")

        return HttpResponse(status=HTTPStatus.ACCEPTED)

    else:
        formulario = AmigosForm(request.GET)
        consulta = formulario.data['consulta'] if 'consulta' in formulario.data else ""
        pagina = request.GET.get('page')

        logger.info("Encontramos los participantes del reto y lo mandamos")
        if consulta != "":
            participantes = Participante.objects.filter(Q(reto__id_reto=id_reto),
                                                        Q(usuario__email__contains=consulta) |
                                                        Q(usuario__nombre__contains=consulta)). \
                exclude(usuario__email=request.user.email).values('usuario')
        else:
            participantes = Participante.objects.filter(Q(reto__id_reto=id_reto)). \
                exclude(usuario__email=request.user.email).values('usuario')

        logger.info("Paginamos los participantes del reto")
        paginator = Paginator(participantes, 3)

        logger.info("Obtenemos los participantes de la página indicada")

        try:
            participantes = paginator.get_page(pagina)
        except PageNotAnInteger:
            participantes = paginator.get_page(1)
        except EmptyPage:
            participantes = paginator.get_page(1)

        return render(request, "YoPuedo/elementos/modal-participantes.html",
                      {'participantes': participantes})


##########################################################################################

# Función para eliminar el animador del reto
@login_required
def animador_reto(request, id_reto):
    logger.info("Comprobamos que existe el reto")
    reto = get_object_or_404(Reto, id_reto=id_reto)

    logger.info(f"Eliminamos al animador del reto {id_reto}")
    Animador.objects.filter(reto=reto, usuario=request.user).delete()

    return redirect('/mis_retos/')


##########################################################################################

# Función para mostrar el error 404
def page_not_found(request):
    render(request, '404.html', status=404)
