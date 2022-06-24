from django.test import TestCase
from ..forms import Registro
from TFM.settings import BASE_DIR


# Comprobamos la validación del formulario de registro
class RegistroFormTests(TestCase):
    def test_campos_vacios(self):
        form_data = {
            'email': '',
            'nombre': '',
            'password': '',
            'password_again': '',
        }

        form = Registro(data=form_data)

        self.assertEqual(form.errors['email'], ['Este campo es obligatorio.'])
        self.assertEqual(form.errors['nombre'], ['Este campo es obligatorio.'])
        self.assertEqual(form.errors['password'], ['Este campo es obligatorio.'])
        self.assertEqual(form.errors['password_again'], ['Este campo es obligatorio.'])
        self.assertEqual(form.errors['foto_de_perfil'], ['Este campo es obligatorio.'])

    def test_email_incorrecto(self):
        form_data = {
            'email': 'mariajesus',
            'nombre': 'María Jesús',
            'password': 'Password1*',
            'password_again': 'Password1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"

        form = Registro(data=form_data, files={'foto_de_perfil': open(foto_perfil, 'rb')})

        self.assertEqual(form.errors['email'], ['Introduzca una dirección de correo '
                                                'electrónico válida.'])

    def test_nombre_largo(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús López Salmerón María Jesús López Salmerón María '
                      'Jesús López Salmerón María Jesús López Salmerón',
            'password': 'Password1*',
            'password_again': 'Password1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"

        form = Registro(data=form_data, files={'foto_de_perfil': open(foto_perfil, 'rb')})

        self.assertEqual(form.errors['nombre'], ["Debe tener como máximo de 100 "
                                                   "caracteres"])

    def test_no_coinciden_password(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password1*',
            'password_again': 'Password1',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"

        form = Registro(data=form_data, files={'foto_de_perfil': open(foto_perfil, 'rb')})

        self.assertEqual(form.errors['password_again'], ['Las contraseñas deben ser '
                                                         'iguales'])

    def test_password_no_numerico(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password*',
            'password_again': 'Password*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"

        form = Registro(data=form_data, files={'foto_de_perfil': open(foto_perfil, 'rb')})

        self.assertEqual(form.errors['password'], ['La contraseña debe contener al menos '
                                                   'un número'])

    def test_password_no_mayuscula(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'password1*',
            'password_again': 'password1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"

        form = Registro(data=form_data, files={'foto_de_perfil': open(foto_perfil, 'rb')})

        self.assertEqual(form.errors['password'], ['La contraseña debe tener al menos '
                                                   'una mayúscula'])

    def test_password_no_simbolos(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password1',
            'password_again': 'Password1',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"

        form = Registro(data=form_data, files={'foto_de_perfil': open(foto_perfil, 'rb')})

        self.assertEqual(form.errors['password'], ["La contraseña debe tener al menos "
                                                   "uno de estos símbolos: "
                                                   "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"])

    def test_password_no_minuscula(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'PASSWORD1*',
            'password_again': 'PASSWORD1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"

        form = Registro(data=form_data, files={'foto_de_perfil': open(foto_perfil, 'rb')})

        self.assertEqual(form.errors['password'],
                         ["La contraseña debe contener al menos una letra "
                          "en minúscula"])

    def test_password_corta(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Pwd1*',
            'password_again': 'Pwd1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"

        form = Registro(data=form_data, files={'foto_de_perfil': open(foto_perfil, 'rb')})

        self.assertEqual(form.errors['password'], ["Debe tener como mínimo de 8 "
                                                   "caracteres"])

    def test_password_larga(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'PwdPassword1*_^0j',
            'password_again': 'PwdPassword1*_^0j',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"

        form = Registro(data=form_data, files={'foto_de_perfil': open(foto_perfil, 'rb')})

        self.assertEqual(form.errors['password'], ["Debe tener como máximo de 16 "
                                                   "caracteres"])

    def test_no_imagen(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password1*',
            'password_again': 'Password1',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/prueba.txt"

        form = Registro(data=form_data, files={'foto_de_perfil': open(foto_perfil, 'rb')})

        self.assertEqual(form.errors['foto_de_perfil'], ['Envíe una imagen válida. El '
                                                         'fichero que ha enviado no era '
                                                         'una imagen o se trataba de una '
                                                         'imagen corrupta.'])
