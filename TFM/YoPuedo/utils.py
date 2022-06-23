import errno
import logging
import os.path

logger = logging.getLogger(__name__)


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
