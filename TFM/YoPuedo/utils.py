import logging
import os.path
from TFM.settings import BASE_DIR
from .forms import RegistroForm
from .models import Usuario

logger = logging.getLogger(__name__)


class Utils:
    # Método de subida de ficheros
    @staticmethod
    def handle_uploaded_file(image, localizacion, directorio):
        logger.info("Comprobamos que el directorio donde se va a guardar está creado "
                    "previamente")
        if not os.path.exists(directorio):
            try:
                logger.info(f"Creamos el directorio {directorio}")
                os.makedirs(directorio)
            except OSError:
                logger.error(
                    f"Se ha producido un error al crear el directorio {directorio}")
                raise

        logger.info("Guardamos archivos en local")
        with open(localizacion, "wb+") as destination:
            for chunk in image.chunks():
                destination.write(chunk)

    # Método para guardar al nuevo usuario en la BBDD
    @staticmethod
    def guardar_usuario(self, request):
        form = RegistroForm(request.POST, request.FILES)

        email = form.cleaned_data['email'].value()
        nombre = form.cleaned_data['nombre'].value()
        password = form.cleaned_data['password'].value()
        foto = request.FILES["foto_de_perfil"]
        fichero, extension = os.path.splitext(foto.name)
        directorio = os.path.join(BASE_DIR, "media", "YoPuedo", "foto_perfil")
        localizacion = os.path.join(directorio, email + extension)
        clave_fija = self.claves_aleatorias(16)
        clave_aleatoria = self.claves_aleatorias(10)

        try:
            self.handle_uploaded_file(foto, localizacion, directorio)
        except:
            logger.error("Error al subir la foto de perfil")

        Usuario.objects.create(email=email, nombre=nombre, password=password,
                               fotoPerfil=localizacion, claveFija=clave_fija,
                               claveAleatoria=clave_aleatoria)
        return clave_aleatoria, clave_fija

    # Método que genera claves aleatorias
    @staticmethod
    def claves_aleatorias(longitud):
        logger.info("Generamos clave aleatoria")
        return "numero"

    # Método para enviar correo con las claves aleatorias
    @staticmethod
    def enviar_clave(clave_aleatoria,email):
        logger.info("Enviamos correo con las claves aleatorias")

    # Método para enviar correo con las claves fijas
    @staticmethod
    def enviar_clave_fija(clave_fija, email):
        logger.info("Enviamos correo con las claves aleatorias")
