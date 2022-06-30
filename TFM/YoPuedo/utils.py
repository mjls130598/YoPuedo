import logging
import os.path
from TFM.settings import BASE_DIR
from TFM.YoPuedo.forms import RegistroForm
from TFM.YoPuedo.models import Usuario

logger = logging.getLogger(__name__)


# Función de subida de ficheros
def handle_uploaded_file(image, localizacion, directorio):
    logger.info("Comprobamos que el directorio donde se va a guardar está creado "
                "previamente")
    if not os.path.exists(directorio):
        try:
            logger.info(f"Creamos el directorio {directorio}")
            os.makedirs(directorio)
        except OSError:
            logger.error(f"Se ha producido un error al crear el directorio {directorio}")
            raise

    logger.info("Guardamos archivos en local")
    with open(localizacion, "wb+") as destination:
        for chunk in image.chunks():
            destination.write(chunk)


# Función para guardar al nuevo usuario en la BBDD
def guardar_usuario(request):
    form = RegistroForm(request.POST, request.FILES)

    email = form.cleaned_data['email'].value()
    nombre = form.cleaned_data['nombre'].value()
    password = form.cleaned_data['password'].value()
    foto = request.FILES["foto_de_perfil"]
    fichero, extension = os.path.splitext(foto.name)
    directorio = os.path.join(BASE_DIR, "media", "YoPuedo", "foto_perfil")
    localizacion = os.path.join(directorio, email + extension)

    try:
        handle_uploaded_file(foto, localizacion, directorio)
    except:
        logger.error("Error al subir la foto de perfil")

    Usuario.objects.create(email=email, nombre=nombre,
                           password=password,
                           fotoPerfil=localizacion)

# Función que genera claves aleatorias
def claves_aleatorias():
    logger.info("Generamos clave aleatoria")
