import logging
import mimetypes
import os

logger = logging.getLogger(__name__)


def checkear_imagen(fichero):
    guess = mimetypes.guess_type(fichero)
    logger.info(f"Tipo del {fichero}: {guess}")
    return guess == "image/jpeg" or guess == "image/png"


def handle_uploaded_file(f, localizacion):
    logger.info("Guardamos archivos en local")
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), localizacion),
              'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            logger.info("Guardado " + localizacion)
