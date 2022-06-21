import logging
import os

logger = logging.getLogger(__name__)


def handle_uploaded_file(f, localizacion):
    logger.info("Guardamos archivos en local")
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), localizacion),
              'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            logger.info("Guardado " + localizacion)
