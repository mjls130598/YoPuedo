import logging
import os.path
import random
import string

from TFM.settings import BASE_DIR, EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives

from .models import Usuario, Reto, Etapa

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

        fichero = os.path.join("/media", "YoPuedo", "foto_perfil", email + extension)
        Usuario.objects.create_user(email=email, nombre=nombre, password=password,
                                    foto_perfil=fichero, clave_fija=clave_fija,
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
        ("", ""),
        ("economia", "Ahorro"),
        ("inteligencia", "Conocimientos"),
        ("salud", "Deporte"),
        ("mente", "Miedos")
    )

    categorias = ["economia", "inteligencia", "salud", "mente"]

    @staticmethod
    def numero_elementos_importados(importados):

        num_elementos = 0

        for elemento in importados:
            if elemento:
                num_elementos += 1

        return num_elementos

    @staticmethod
    def crear_id_reto():
        caracteres = string.ascii_lowercase + string.digits
        id_reto = "RET"
        while True:
            id_reto += ''.join(random.choice(caracteres) for _ in range(47))
            reto = Reto.objects.filter(id_reto=id_reto)

            if len(reto) == 0:
                break
            else:
                id_reto = "RET"

        return id_reto

    @staticmethod
    def crear_id_etapa():
        caracteres = string.ascii_lowercase + string.digits
        id_etapa = "ETP"
        while True:
            id_etapa += ''.join(random.choice(caracteres) for _ in range(47))
            etapa = Etapa.objects.filter(id_etapa=id_etapa)

            if len(etapa) == 0:
                break
            else:
                id_etapa = "ETP"

        return id_etapa
