import logging
import os.path
import random
import string

from TFM.settings import BASE_DIR, EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives

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
    def guardar_usuario(self, email, nombre, password, foto):
        fichero, extension = os.path.splitext(foto.name)
        directorio = os.path.join(BASE_DIR, "media", "YoPuedo", "foto_perfil")
        localizacion = os.path.join(directorio, email + extension)
        clave_fija = self.claves_aleatorias(16)
        clave_aleatoria = self.claves_aleatorias(10)

        try:
            self.handle_uploaded_file(foto, localizacion, directorio)
        except:
            logger.error("Error al subir la foto de perfil")

        Usuario.objects.create_user(email=email, nombre=nombre, password=password,
                                    foto_perfil=localizacion, clave_fija=clave_fija,
                                    clave_aleatoria=clave_aleatoria)
        return clave_aleatoria, clave_fija

    # Método que genera claves aleatorias
    @staticmethod
    def claves_aleatorias(longitud):
        logger.info("Generamos clave aleatoria")
        letters = string.ascii_letters
        result_str = ''.join(random.choice(letters) for i in range(longitud))
        return result_str

    # Método para enviar correos
    @staticmethod
    def enviar_correo(content, email, contexto):
        logger.info(f"Enviamos correo a {email}")
        mail = EmailMultiAlternatives(
            contexto,
            'Yo Puedo',
            EMAIL_HOST_USER,
            [email]
        )

        mail.attach_alternative(content, 'text/html')
        mail.send()

    CATEGORIAS_CHOOSE = (
        ("economia", "Ahorro"),
        ("inteligencia", "Conocimientos"),
        ("salud", "Deporte"),
        ("mente", "Miedos")
    )
