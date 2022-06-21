import logging
import mimetypes

logger = logging.getLogger(__name__)


def checkear_imagen(fichero):
    guess = mimetypes.guess_type(fichero)
    logger.info(f"Tipo del {fichero}: {guess}")
    return guess == "image/jpeg"  # or guess == "image/png"
