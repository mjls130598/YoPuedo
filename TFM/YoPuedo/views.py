import logging
import os
from http import HTTPStatus
from itertools import chain

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template

from .utils import Utils
from .forms import RegistroForm, InicioForm, ClaveForm, RetoGeneralForm, RetoEtapaForm, \
    AmigosForm, EtapasFormSet, PruebaForm, AnimoForm, PerfilForm
from .models import Usuario, Amistad, Reto, Etapa, Animador, Participante, Calificacion, \
    Prueba, Animo

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
            elif tipo == 'eliminar':
                logger.info('Eliminamos el usuario')
                logout(request)
                Usuario.objects.get(email=email).delete()
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
            propuestos = Reto.objects.annotate(cnt=Count('participante')). \
                filter(estado='Propuesto', coordinador=request.user, cnt=1) \
                if tipo == 'individuales' else \
                Reto.objects.annotate(cnt=Count('participante')). \
                    filter(Q(estado='Propuesto'),
                           Q(participante__usuario=request.user), cnt__gt=1)

        else:
            propuestos = Reto.objects.annotate(cnt=Count('participante')). \
                filter(estado='Propuesto', coordinador=request.user, cnt=1) \
                if tipo == 'individuales' else \
                Reto.objects.annotate(cnt=Count('participante')). \
                    filter(Q(estado='Propuesto'),
                           Q(participante__usuario=request.user), cnt__gt=1)

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
            retos = Reto.objects.annotate(cnt=Count('participante')). \
                filter(estado='Propuesto', coordinador=request.user, cnt=1) \
                if tipo == 'individuales' else \
                Reto.objects.annotate(cnt=Count('participante')). \
                    filter(Q(estado='Propuesto'),
                           Q(participante__usuario=request.user), cnt__gt=1)

        elif estado == "proceso":
            retos = Reto.objects.annotate(cnt=Count('participante')). \
                filter(estado='En proceso', coordinador=request.user, cnt=1) \
                if tipo == 'individuales' else \
                Reto.objects.annotate(cnt=Count('participante')). \
                    filter(Q(estado='En proceso'),
                           Q(participante__usuario=request.user), cnt__gt=1)

        elif estado == "finalizados":
            retos = Reto.objects.annotate(cnt=Count('participante')). \
                filter(estado='Finalizado', coordinador=request.user, cnt=1) \
                if tipo == 'individuales' else \
                Reto.objects.annotate(cnt=Count('participante')). \
                    filter(Q(estado='Finalizado'),
                           Q(participante__usuario=request.user), cnt__gt=1)

        elif estado == "animando":
            retos = Reto.objects.annotate(cnt=Count('participante')). \
                filter(Q(animador__usuario=request.user), cnt=1) \
                if tipo == 'individuales' else \
                Reto.objects.annotate(cnt=Count('participante')). \
                    filter(Q(animador__usuario=request.user), cnt__gt=1)

    else:
        if estado == "propuestos":
            retos = Reto.objects.annotate(cnt=Count('participante')). \
                filter(estado='Propuesto', coordinador=request.user,
                       categoria=categoria, cnt=1) \
                if tipo == 'individuales' else \
                Reto.objects.annotate(cnt=Count('participante')). \
                    filter(Q(estado='Propuesto'),
                           Q(participante__usuario=request.user),
                           Q(categoria=categoria), cnt__gt=1)

        elif estado == "proceso":
            retos = Reto.objects.annotate(cnt=Count('participante')). \
                filter(estado='En proceso', coordinador=request.user,
                       categoria=categoria, cnt=1) \
                if tipo == 'individuales' else \
                Reto.objects.annotate(cnt=Count('participante')). \
                    filter(Q(estado='En proceso'),
                           Q(participante__usuario=request.user),
                           Q(categoria=categoria), cnt__gt=1)

        elif estado == "finalizados":
            retos = Reto.objects.annotate(cnt=Count('participante')). \
                filter(estado='Finalizado', coordinador=request.user,
                       categoria=categoria, cnt=1) \
                if tipo == 'individuales' else \
                Reto.objects.annotate(cnt=Count('participante')). \
                    filter(Q(estado='Finalizado'),
                           Q(participante__usuario=request.user),
                           Q(categoria=categoria), cnt__gt=1)

        elif estado == "animando":
            retos = \
                Reto.objects.annotate(cnt=Count('participante')). \
                    filter(animador__usuario=request.user, categoria=categoria, cnt=1) \
                    if tipo == 'individuales' else \
                    Reto.objects.annotate(cnt=Count('participante')). \
                        filter(animador__usuario=request.user, categoria=categoria,
                               cnt__gt=1)

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

            # Comprobamos si la parte principal es correcto
            if general_form.is_valid() and etapas_form.is_valid():
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
                    id_etapa = Utils.crear_id_etapa(index)
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

                logger.info("Guardamos COORDINADOR como PARTICIPANTE")
                participante = Participante()
                participante.save()
                participante.reto.add(reto)
                participante.usuario.add(request.user)
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

    anima = reto.animador_set.filter(usuario=request.user).exists()
    participa = reto.participante_set.filter(usuario=request.user).exists()

    logger.info("Comprobamos que el reto sea de la persona que lo está viendo")
    if anima or participa:
        logger.info(f"Recogemos las etapas del reto {id_reto}")
        etapas = reto.etapa_set.all()

        logger.info(f"Miramos los animadores del reto {id_reto}")
        animadores = reto.animador_set.all().exclude(usuario=request.user)

        logger.info("Modificamos la información obtenida de los animadores para" +
                    " mandarla a frontend")
        animadores_finales = []

        for animador in animadores:
            animadores_finales.append({
                'usuario': animador.usuario.first(),
                'superanimador': animador.superanimador})

        logger.info(f"Devolvemos los participantes del reto {id_reto}")
        participantes = reto.participante_set.all().exclude(usuario=request.user)

        logger.info(
            "Modificamos la información obtenida de los participantes para mandarla " +
            "a frontend")
        participantes_finales = []

        for participante in participantes:
            participantes_finales.append(participante.usuario.first())

        calificaciones = {}

        if participa:
            participante = reto.participante_set.filter(usuario=request.user).first()
            for etapa in etapas:
                calificaciones[etapa.id_etapa] = etapa.calificacion_set. \
                    filter(participante=participante).first().calificacion \
                    if etapa.calificacion_set.filter(participante=participante).exists() \
                    else ""

        return render(request, 'YoPuedo/reto.html',
                      {'reto': reto, 'etapas': etapas, 'animadores': animadores_finales,
                       'participantes': participantes_finales, 'participa': participa,
                       'calificaciones': calificaciones})

    else:
        logger.error("No forma parte del reto")
        raise PermissionDenied


##########################################################################################

# Función para iniciar el reto
@login_required
def iniciar_reto(request, id_reto):
    logger.info(f"Iniciamos el reto {id_reto}")
    reto = get_object_or_404(Reto, id_reto=id_reto)

    logger.info("Comprobamos que el reto sea de la persona que lo está viendo")
    if reto.coordinador == request.user:
        reto.estado = "En proceso"
        reto.save()

        logger.info("Iniciamos la primera etapa del reto")
        etapa = reto.etapa_set.first()
        etapa.estado = "En proceso"
        etapa.save()

        logger.info(f"Redirigimos a la página del reto")
        return redirect(f"/reto/{id_reto}")

    else:
        logger.error("No forma parte del reto")
        raise PermissionDenied


##########################################################################################

# Función para editar el reto
@login_required
def editar_reto(request, id_reto):
    logger.info("Comprobamos que existe el reto")
    reto = get_object_or_404(Reto, id_reto=id_reto)

    logger.info("Comprobamos que el reto sea de la persona que lo está viendo")
    if reto.coordinador == request.user and reto.estado == 'Propuesto':
        logger.info("Recogemos el resto de información de un reto")
        animadores_reto = reto.animador_set.all()
        animadores = []

        for animador in animadores_reto:
            animadores.append({
                'usuario': animador.usuario.first(),
                'superanimador': str(animador.superanimador).lower()})

        participantes_reto = reto.participante_set.all()
        participantes = []
        for participante in participantes_reto:
            participantes.append(participante.usuario.first())

        max_etapas = 5
        errores = False
        etapas_validas = True
        etapas_form_model = formset_factory(RetoEtapaForm, formset=EtapasFormSet,
                                            max_num=max_etapas)
        etapas = reto.etapa_set.all()

        imagen_objetivo = ""
        audio_objetivo = ""
        video_objetivo = ""

        if "/media/" in reto.objetivo:
            if "jpg" in reto.objetivo or "jpeg" in reto.objetivo or "png" in \
                    reto.objetivo or "svg" in reto.objetivo or "gif" in \
                    reto.objetivo:
                imagen_objetivo = reto.objetivo.split("/")[-1]
            elif "mp3" in reto.objetivo or "acc" in reto.objetivo or "ogg" in \
                    reto.objetivo or "wma" in reto.objetivo:
                audio_objetivo = reto.objetivo.split("/")[-1]
            elif "mp4" in reto.objetivo or "ogg" in reto.objetivo:
                video_objetivo = reto.objetivo.split("/")[-1]

        imagen_recompensa = ""
        audio_recompensa = ""
        video_recompensa = ""

        if "/media/" in reto.recompensa:
            if "jpg" in reto.recompensa or "jpeg" in reto.recompensa or "png" in \
                    reto.recompensa or "svg" in reto.recompensa or "gif" in \
                    reto.recompensa:
                imagen_recompensa = reto.recompensa.split("/")[-1]
            elif "mp3" in reto.recompensa or "acc" in reto.recompensa or "ogg" in \
                    reto.recompensa or "wma" in reto.recompensa:
                audio_recompensa = reto.recompensa.split("/")[-1]
            elif "mp4" in reto.recompensa or "ogg" in reto.recompensa:
                video_recompensa = reto.recompensa.split("/")[-1]

        etapas_objetivo = {}

        for etapa in etapas:
            imagen_objetivo = ""
            audio_objetivo = ""
            video_objetivo = ""

            if "jpg" in etapa.objetivo or "jpeg" in etapa.objetivo or "png" in \
                    etapa.objetivo or "svg" in etapa.objetivo or "gif" in \
                    etapa.objetivo:
                imagen_objetivo = etapa.objetivo.split("/")[-1]
            elif "mp3" in etapa.objetivo or "acc" in etapa.objetivo or "ogg" in \
                    etapa.objetivo or "wma" in etapa.objetivo:
                audio_objetivo = etapa.objetivo.split("/")[-1]
            elif "mp4" in etapa.objetivo or "ogg" in etapa.objetivo:
                video_objetivo = etapa.objetivo.split("/")[-1]

            etapas_objetivo[etapa.id_etapa] = {'objetivo_imagen': imagen_objetivo,
                                               'objetivo_audio': audio_objetivo,
                                               'objetivo_video': video_objetivo}

        if request.method == 'GET':
            logger.info("Entramos en la parte GET de EDITAR RETO")

            data = {'titulo': reto.titulo}

            logger.info("Recogemos el tipo de objetivo del reto guardado")
            if not "/media/" in reto.objetivo:
                data['objetivo_texto'] = reto.objetivo

            logger.info("Recogemos el tipo de recompensa del reto guardado")
            if not "/media/" in reto.recompensa:
                data['recompensa_texto'] = reto.recompensa

            logger.info("Recogemos la categoría del reto")
            data['categoria'] = reto.categoria

            logger.info("Guardamos los datos del reto recogidos y lo mandamos a su " +
                        "formulario")
            general_form = RetoGeneralForm(data=data)

            logger.info("Eliminamos los errores generados en la parte GENERAL")
            if "/media/" in reto.objetivo:
                general_form.errors.pop('objetivo_texto', None)
            if "/media/" in reto.recompensa:
                general_form.errors.pop('recompensa_texto', None)

            logger.info("Recogemos la información de cada una de las etapas")
            data = {
                # Etapas
                'form-INITIAL_FORMS': '0',
                'form-TOTAL_FORMS': len(etapas),
                'form-MAX_NUM_FORMS': max_etapas,
            }

            for index, etapa in enumerate(etapas):
                logger.info("Recogemos el tipo de objetivo de la etapa guardado")
                data[f'form-{index}-id_etapa'] = etapa.id_etapa

                if not "/media/" in etapa.objetivo:
                    data[f'form-{index}-objetivo_texto'] = etapa.objetivo

            etapas_form = etapas_form_model(data)

            logger.info("Borramos los errores dentro de ETAPAS")
            for index, etapa_form in enumerate(etapas_form):
                if "/media/" in etapas[index].objetivo:
                    etapa_form.errors.pop('objetivo_texto', None)

        if request.method == 'POST':
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
            general_form, valido_general = Utils.valido_general(reto, general_form)

            etapas_form = etapas_form_model(request.POST, request.FILES)
            etapas_form, etapas_validas = Utils.validas_etapas(reto, etapas_form)
            # Comprobamos si la parte principal es correcto
            if valido_general and etapas_validas:
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
                        Utils.handle_uploaded_file(objetivo_multimedia, localizacion,
                                                   directorio)
                    except:
                        logger.error("Error al subir el objetivo")
                else:
                    objetivo = objetivo_texto if objetivo_texto != "" else reto.objetivo

                if objetivo != reto.objetivo and "/media/" in reto.objetivo:
                    logger.info("Borramos el antiguo objetivo del reto")
                    Utils.eliminar_archivo(os.path.join(BASE_DIR, reto.objetivo[1:]))

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
                            Utils.handle_uploaded_file(recompensa_multimedia,
                                                       localizacion,
                                                       directorio)
                        except:
                            logger.error("Error al subir la recompensa")
                else:
                    recompensa = recompensa_texto if recompensa_texto != "" else reto.recompensa

                if recompensa != reto.recompensa and "/media/" in reto.recompensa:
                    logger.info("Borramos la antigua recompensa del reto")
                    Utils.eliminar_archivo(os.path.join(BASE_DIR, reto.recompensa[1:]))

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
                        id_etapa = Utils.crear_id_etapa(index)
                        logger.info(f"NUEVA ETAPA {id_etapa}")

                        Etapa(id_etapa=id_etapa, reto=reto, objetivo=objetivo).save()
                    else:
                        etapas_ids.remove(id_etapa)
                        etapa = Etapa.objects.get(id_etapa=id_etapa)
                        if objetivo != "" and objetivo != etapa.objetivo and "/media/" \
                                in etapa.objetivo:
                            logger.info(
                                f"Borramos el antiguo objetivo de la etapa {id_etapa}")
                            Utils.eliminar_archivo(
                                os.path.join(BASE_DIR, etapa.objetivo[1:]))
                        etapa.objetivo = objetivo if objetivo != "" else etapa.objetivo
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
                animadores = []
                participantes = []

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
                       "participantes": participantes,
                       "error_etapas": not etapas_validas,
                       "objetivo_imagen": imagen_objetivo,
                       "objetivo_audio": audio_objetivo,
                       "objetivo_video": video_objetivo,
                       "recompensa_imagen": imagen_recompensa,
                       "recompensa_audio": audio_recompensa,
                       "recompensa_video": video_recompensa,
                       "etapas_objetivo": etapas_objetivo,
                       "id_reto": id_reto})

    else:
        logger.error("No forma parte del reto")
        raise PermissionDenied


##########################################################################################

# Función para eliminar el reto
@login_required
def eliminar_reto(request, id_reto):
    logger.info("Comprobamos que existe el reto")
    reto = get_object_or_404(Reto, id_reto=id_reto)

    logger.info("Comprobamos que el reto sea de la persona que lo está viendo")
    if reto.coordinador == request.user:
        logger.info(f"Eliminamos el reto {id_reto}")
        reto.delete()

        logger.info(f"Redirigimos a la página de mis retos")
        return redirect(f"/mis_retos/")

    else:
        logger.error("No forma parte del reto")
        raise PermissionDenied


##########################################################################################

# Función para cambiar el coordinador del reto
@login_required
def coordinador_reto(request, id_reto):
    logger.info("Comprobamos que existe el reto")
    reto = get_object_or_404(Reto, id_reto=id_reto)

    logger.info("Comprobamos que el reto sea de la persona que lo está viendo")
    if reto.coordinador == request.user:
        if request.method == 'POST':
            coordinador = request.POST.get('coordinador')

            if coordinador != "":
                logger.info(f"Cambiamos el coordinador por {coordinador}")
                reto.coordinador = Usuario.objects.get(email=coordinador)
                reto.save()

                logger.info(f"Redirigimos con un status {HTTPStatus.ACCEPTED}")

            return HttpResponse(status=HTTPStatus.ACCEPTED)

        else:
            formulario = AmigosForm(request.GET)
            consulta = formulario.data['consulta'] if 'consulta' in formulario.data \
                else ""
            pagina = request.GET.get('page')

            logger.info("Encontramos los participantes del reto y lo mandamos")
            participantes = reto.participante_set. \
                filter(Q(usuario__email__contains=consulta) |
                       Q(usuario__nombre__contains=consulta)). \
                exclude(usuario=request.user).annotate(email=F('usuario__email'),
                                                       foto_perfil=F(
                                                           'usuario__foto_perfil'),
                                                       nombre=F('usuario__nombre')) \
                .values('email', 'foto_perfil', 'nombre') \
                if consulta != "" \
                else reto.participante_set.exclude(usuario=request.user). \
                annotate(email=F('usuario__email'),
                         foto_perfil=F('usuario__foto_perfil'),
                         nombre=F('usuario__nombre')) \
                .values('email', 'foto_perfil', 'nombre')

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
                          {'participantes': participantes, 'form_consulta': formulario})

    else:
        logger.error("No forma parte del reto")
        raise PermissionDenied


##########################################################################################

# Función para eliminar el animador del reto
@login_required
def animador_reto(request, id_reto):
    logger.info("Comprobamos que existe el reto")
    reto = get_object_or_404(Reto, id_reto=id_reto)

    logger.info("Comprobamos que el reto sea de la persona que lo está viendo")
    if reto.animador_set.filter(usuario=request.user).exists():
        logger.info(f"Eliminamos al animador del reto {id_reto}")
        Animador.objects.filter(reto=reto, usuario=request.user).delete()

        return redirect('/mis_retos/')

    else:
        logger.error("No forma parte del reto")
        raise PermissionDenied


##########################################################################################

# Función para calificar una etapa
@login_required
def calificar_etapa(request, id_etapa):
    logger.info("Comprobamos que existe esa etapa")
    etapa = get_object_or_404(Etapa, id_etapa=id_etapa)

    logger.info("Comprobamos que clasifica una persona que sea del reto")
    if etapa.reto.participante_set.filter(usuario=request.user).exists():

        logger.info("Recogemos la calificación de esa persona")
        puntuacion = request.GET.get('calificacion')

        if puntuacion != "":
            logger.info("Guardamos calificación de la etapa")
            participante = etapa.reto.participante_set.get(usuario=request.user)
            calificacion = etapa.calificacion_set.filter(participante=participante)

            if not calificacion.exists():
                logger.info("Creamos una nueva calificación")
                calificacion = Calificacion()
                calificacion.save()
                calificacion.etapa.add(etapa)
                calificacion.participante.add(participante)

            else:
                logger.info("Cogemos la calificación ya creada")
                calificacion = calificacion.first()

            calificacion.calificacion = puntuacion
            calificacion.save()

            calificaciones = etapa.calificacion_set.all()
            participantes = etapa.reto.participante_set.all()

            # Si todos los participantes han calificado la etapa, ...
            if len(calificaciones) == len(participantes) and etapa.estado != 'Finalizado':
                logger.info("Modificamos el estado de esa etapa")
                etapa.estado = 'Finalizado'
                etapa.save()

                etapas = etapa.reto.etapa_set.all()

                # Si es la última etapa, modificamos el estado del reto a "Finalizado"
                logger.info("Miramos si es la última etapa del reto")
                if etapa == etapas.last():
                    logger.info("Se actualiza el estado del reto")
                    etapa.reto.estado = 'Finalizado'
                    etapa.reto.save()

                # Sino, modificamos la siguiente etapa a "En proceso"
                else:
                    logger.info("Actualizamos la siguiente etapa")
                    etapas = list(etapas)
                    num_etapa = etapas.index(etapa)
                    siguiente_etapa = etapa.reto.etapa_set.all()[num_etapa + 1]
                    siguiente_etapa.estado = 'En proceso'
                    siguiente_etapa.save()

            logger.info(f"Devolvemos el estado {HTTPStatus.CREATED}")
            return HttpResponse(status=HTTPStatus.CREATED)

        logger.info(f'Devolvemos el estado {HTTPStatus.BAD_REQUEST}')
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    else:
        logger.error("No forma parte activa del reto")
        raise PermissionDenied


##########################################################################################

# Función para ver y crear PRUEBAS
@login_required
def pruebas(request, id_etapa):
    logger.info(f"Recogemos los datos de la etapa {id_etapa}")
    etapa = get_object_or_404(Etapa, id_etapa=id_etapa)
    participante = etapa.reto.participante_set.filter(usuario=request.user)

    logger.info("Comprobamos que añade una prueba un participante de la etapa encontrada")
    if participante.exists():
        participante = participante.first()

        if request.method == 'POST' and etapa.estado == 'En proceso':
            logger.info("Entramos en la parte POST de PRUEBAS")
            prueba_form = PruebaForm(request.POST, request.FILES)

            if prueba_form.is_valid():
                logger.info(f"NUEVA PRUEBA EN {id_etapa}")

                prueba_texto = prueba_form.cleaned_data['prueba_texto'].value()
                prueba_imagen = request.FILES["prueba_imagen"] \
                    if 'prueba_imagen' in request.FILES else None
                prueba_audio = request.FILES["prueba_audio"] \
                    if 'prueba_audio' in request.FILES else None
                prueba_video = request.FILES["prueba_video"] \
                    if 'prueba_video' in request.FILES else None

                prueba_multimedia = prueba_imagen if prueba_imagen else (
                    prueba_audio if prueba_audio else prueba_video)

                if prueba_multimedia:
                    directorio = os.path.join(BASE_DIR, "media", "YoPuedo",
                                              etapa.reto.id_reto, "Pruebas")
                    localizacion = os.path.join(directorio, prueba_multimedia.name)
                    prueba_guardar = os.path.join("/media", "YoPuedo",
                                                  etapa.reto.id_reto, "Pruebas",
                                                  prueba_multimedia.name)
                    try:
                        Utils.handle_uploaded_file(prueba_multimedia, localizacion,
                                                   directorio)
                    except:
                        logger.error("Error al subir el objetivo")
                else:
                    prueba_guardar = prueba_texto

                logger.info(f"PRUEBA: {prueba_guardar}")

                logger.info(f"Guardamos prueba en {id_etapa}")
                prueba = Prueba()
                prueba.save()
                prueba.participante.add(participante)
                prueba.etapa.add(etapa)
                prueba.prueba = prueba_guardar
                prueba.save()

                logger.info(f"Devolvemos status {HTTPStatus.CREATED}")
                return HttpResponse(status=HTTPStatus.CREATED,
                                    headers={'HX-Trigger': 'pruebaListaActualizar'})

            else:
                logger.error(f"Error al validar el formulario PRUEBAS de {id_etapa}")

        else:
            logger.info("Entramos en la parte GET de PRUEBAS")
            prueba_form = PruebaForm() if etapa.estado == 'En proceso' else None

        pruebas = etapa.prueba_set.all()

        return render(request, 'YoPuedo/informacion_reto/pruebas.html', {
            'prueba_form': prueba_form,
            'pruebas': pruebas
        })

    else:
        logger.error("No forma la parte activa de PRUEBAS")
        raise PermissionDenied


##########################################################################################

# Función para ver y crear ÁNIMOS
@login_required
def animos(request, id_etapa):
    logger.info(f"Recogemos los datos de la etapa {id_etapa}")
    etapa = get_object_or_404(Etapa, id_etapa=id_etapa)
    participante = etapa.reto.participante_set.filter(usuario=request.user)
    animador = etapa.reto.animador_set.filter(usuario=request.user)

    logger.info("Comprobamos que el participante ve o el animador crea ánimos de la "
                "etapa encontrada")
    if participante.exists() or animador.exists():
        if request.method == 'POST' and etapa.estado == 'En proceso' and animador.exists():
            animador = animador.first()

            logger.info("Entramos en la parte POST de ÁNIMOS")
            animo_form = AnimoForm(request.POST, request.FILES)

            if animo_form.is_valid():
                logger.info(f"NUEVo ÁNIMO EN {id_etapa}")

                animo_texto = animo_form.cleaned_data['animo_texto'].value()
                animo_imagen = request.FILES["animo_imagen"] \
                    if 'animo_imagen' in request.FILES else None
                animo_audio = request.FILES["animo_audio"] \
                    if 'animo_audio' in request.FILES else None
                animo_video = request.FILES["animo_video"] \
                    if 'animo_video' in request.FILES else None

                animo_multimedia = animo_imagen if animo_imagen else (
                    animo_audio if animo_audio else animo_video)

                if animo_multimedia:
                    directorio = os.path.join(BASE_DIR, "media", "YoPuedo",
                                              etapa.reto.id_reto, "Ánimos")
                    localizacion = os.path.join(directorio, animo_multimedia.name)
                    animo_guardar = os.path.join("/media", "YoPuedo",
                                                 etapa.reto.id_reto, "Ánimos",
                                                 animo_multimedia.name)
                    try:
                        Utils.handle_uploaded_file(animo_multimedia, localizacion,
                                                   directorio)
                    except:
                        logger.error("Error al subir el objetivo")
                else:
                    animo_guardar = animo_texto

                logger.info(f"PRUEBA: {animo_guardar}")

                logger.info(f"Guardamos ánimo en {id_etapa}")
                animo = Animo()
                animo.save()
                animo.animador.add(animador)
                animo.etapa.add(etapa)
                animo.mensaje = animo_guardar
                animo.save()

                logger.info(f"Devolvemos status {HTTPStatus.CREATED}")
                return HttpResponse(status=HTTPStatus.CREATED,
                                    headers={'HX-Trigger': 'animosListaActualizar'})

            else:
                logger.error(f"Error al validar el formulario ÁNIMO de {id_etapa}")

        else:
            logger.info("Entramos en la parte GET de PRUEBAS")
            animo_form = AnimoForm() if etapa.estado == 'En proceso' and \
                                        animador.exists() else None

        animador = etapa.reto.animador_set.filter(usuario=request.user,
                                                  superanimador=True)
        animos = etapa.animo_set.all() if participante.exists() or \
                                          animador.exists() else \
            etapa.animo_set.filter(animador=request.user).all()

        return render(request, 'YoPuedo/informacion_reto/animos.html', {
            'animo_form': animo_form,
            'animos': animos
        })

    else:
        logger.error("No forma la parte activa de ÁNIMOS")
        raise PermissionDenied


##########################################################################################

# Función para manejar el perfil de una persona
@login_required
def mi_perfil(request):
    logger.info("Devolvemos los datos de la persona")

    return render(request, "YoPuedo/perfil.html", {
        'foto_perfil': request.user.foto_perfil,
        'nombre': request.user.nombre,
        'email': request.user.email
    })


##########################################################################################

# Función para cerrar sesión a una persona
@login_required
def cerrar_sesion(request):
    logger.info("Cerramos sesión a esta persona")

    logout(request)
    return redirect('/registrarse/')


##########################################################################################

# Función para eliminar a una persona
@login_required
def eliminar(request):
    logger.info("Creamos clave y la mandamos")
    clave = Utils.claves_aleatorias(10)
    request.user.clave_aleatoria = clave
    request.user.save()
    enviar_clave(clave, request.user.email, f"Eliminar la cuenta de "
                                            f"{request.user.nombre} de YoPuedo")

    return render(request, "YoPuedo/perfil.html",
                  {'url': f'/validar_clave/eliminar/{request.user.email}',
                   'foto_perfil': request.user.foto_perfil,
                   'nombre': request.user.nombre,
                   'email': request.user.email
                   })


##########################################################################################

# Función para eliminar a una persona
@login_required
def editar_perfil(request):
    if request.method == 'GET':
        logger.info("Entramos en la parte GET de EDITAR PERFIL")

        # Creamos formulario
        data = {
            'nombre': request.user.nombre
        }
        editar_form = PerfilForm(data=data)

        # Borramos los errores del formulario
        logger.info("Eliminamos los errores creados por el formulario")
        editar_form.errors.pop('password_antigua', None)
        editar_form.errors.pop('password_nueva', None)
        editar_form.errors.pop('password_again', None)
        editar_form.errors.pop('foto_perfil', None)

    else:
        logger.info("Entramos en la parte POST de EDITAR PERFIL")
        editar_form = PerfilForm(request.POST, request.FILES)

        if editar_form.is_valid():
            logger.info("Válido el formulario de EDITAR PERFIL")

            # Eliminamos foto de perfil antigua
            logger.info("Eliminamos la foto de perfil antigua")
            Utils.eliminar_archivo(os.path.join(BASE_DIR, request.user.foto_perfil[1:]))

            # Recogemos los datos del formulario
            contrasena_nueva = editar_form.cleaned_data['password_nueva'].value()
            nombre = editar_form.cleaned_data['nombre'].value()
            foto = request.FILES['foto_perfil']

            # Guardamos foto de perfil nueva
            fichero, extension = os.path.splitext(foto.name)
            directorio = os.path.join(BASE_DIR, "media", "YoPuedo", "foto_perfil")
            localizacion = os.path.join(directorio, request.user.email + extension)

            try:
                Utils.handle_uploaded_file(foto, localizacion, directorio)
            except:
                logger.error("Error al subir la foto de perfil")

            fichero = os.path.join("/media", "YoPuedo", "foto_perfil",
                                   request.user.email + extension)

            # Modificamos el perfil con los datos nuevos
            request.user.set_password(contrasena_nueva)
            request.user.nombre = nombre
            request.user.foto_perfil = fichero
            request.user.save()

            return HttpResponse(HTTPStatus.ACCEPTED)

        else:
            logger.error("El formulario de EDITAR PERFIL tiene errores")

    return render(request, "YoPuedo/editar_perfil.html",
                  {'editar_form': editar_form, })


##########################################################################################

# Función para mostrar el error 404
def page_not_found(request):
    render(request, '404.html', status=404)


##########################################################################################

# Función para mostrar el error 403
def page_not_found(request):
    render(request, '403.html', status=403)
