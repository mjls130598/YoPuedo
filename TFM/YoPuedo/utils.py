import mimetypes


def checkear_imagen(fichero):
    guess = mimetypes.guess_type(fichero)
    return guess == "image/jpeg" or guess == "image/png"
