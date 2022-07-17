import logging
import os.path
import random
import string

from TFM.settings import BASE_DIR
from django.core.mail import send_mail

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

        Usuario.objects.create(email=email, nombre=nombre, password=password,
                               fotoPerfil=localizacion, claveFija=clave_fija,
                               claveAleatoria=clave_aleatoria)
        return clave_aleatoria, clave_fija

    # Método que genera claves aleatorias
    @staticmethod
    def claves_aleatorias(longitud):
        logger.info("Generamos clave aleatoria")
        letters = string.ascii_letters
        result_str = ''.join(random.choice(letters) for i in range(longitud))
        return result_str

    # Método para enviar correo con las claves aleatorias
    @staticmethod
    def enviar_clave(clave_aleatoria, email):
        logger.info(f"Enviamos correo con la clave aleatoria al {email}")
        send_mail('YoPuedo - Verificación de persona',
                  f'''El siguiente conjunto de caracteres son para verificar que eres tú 
                  el que quiere realizar una acción sobre la aplicación YoPuedo. Para 
                  cerciorarnos que eres tú, debes escribir en la aplicación el 
                  siguiente código: {clave_aleatoria}''',
                  None, [email], fail_silently=False)

    # Método para enviar correo con las claves fijas
    @staticmethod
    def enviar_clave_fija(clave_fija, email):
        logger.info(f"Enviamos correo con la clave fija del usuario {email}")
        send_mail('YoPuedo - Verificación de persona',
                  f'''El siguiente conjunto de caracteres son para verificar que eres tú 
                  cuando no te llegue el correo electrónico con una clave aleatoria 
                  introduciéndola en la aplicación cuando sea necesario. 
                  Por favor, guarda en un lugar seguro la siguiente clave: {clave_fija}''',
                  None, [email], fail_silently=False)
