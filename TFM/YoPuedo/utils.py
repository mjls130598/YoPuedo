import logging
import os

logger = logging.getLogger(__name__)


def handle_uploaded_file(image, localizacion):
    logger.info("Guardamos archivos en local")
    with open(localizacion, "wb+") as destination:
        for chunk in image.chunks():
            destination.write(chunk)
