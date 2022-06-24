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
            'foto_de_perfil': ''
        }
        form = Registro(form_data)

        self.assertEqual(form.errors['email'], 'Este campo es obligatorio.')
        self.assertEqual(form.errors['nombre'], 'Este campo es obligatorio.')
        self.assertEqual(form.errors['password'], 'Este campo es obligatorio.')
        self.assertEqual(form.errors['password_again'], 'Este campo es obligatorio.')
        self.assertEqual(form.errors['foto_de_perfil'], 'Este campo es obligatorio.')

    def test_email_incorrecto(self):
        form_data = {
            'email': 'mariajesus',
            'nombre': 'María Jesús',
            'password': 'Password1*',
            'password_again': 'Password1*',
            'foto_de_perfil': f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        }
        form = Registro(form_data)

        self.assertEqual(form.errors['email'], 'Introduzca una dirección de correo '
                                               'correcta')

    def test_no_coinciden_password(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password*',
            'password_again': 'Password1*',
            'foto_de_perfil': f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        }
        form = Registro(form_data)

        self.assertEqual(form.errors['password_again'], 'Las contraseñas deben ser '
                                                        'iguales')

    def test_password_no_numerico(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password*',
            'password_again': 'Password*',
            'foto_de_perfil': f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        }
        form = Registro(form_data)

        self.assertEqual(form.errors['password'], 'La contraseña debe contener al menos '
                                                  'un número')

    def test_password_no_mayuscula(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'password*',
            'password_again': 'password*',
            'foto_de_perfil': f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        }
        form = Registro(form_data)

        self.assertEqual(form.errors['password'], 'La contraseña debe tener al menos '
                                                  'una mayúscula')

    def test_password_no_simbolos(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password1',
            'password_again': 'Password1',
            'foto_de_perfil': f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        }
        form = Registro(form_data)

        self.assertEqual(form.errors['password'], "La contraseña debe tener al menos "
                                                  "uno de estos símbolos: "
                                                  "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?")

    def test_password_no_minuscula(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'PASSWORD1*',
            'password_again': 'PASSWORD1*',
            'foto_de_perfil': f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        }
        form = Registro(form_data)

        self.assertEqual(form.errors['password'],
                         "La contraseña debe contener al menos una letra "
                         "en minúscula")

    def test_no_imagen(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password1*',
            'password_again': 'Password1*',
            'foto_de_perfil': f"{BASE_DIR}/media/YoPuedo/foto_perfil/prueba.txt"
        }
        form = Registro(form_data)

        self.assertEqual(form.errors['foto_de_perfil'], 'Envíe una imagen válida. El '
                                                        'fichero que ha enviado no era '
                                                        'una imagen o se trataba de una '
                                                        'imagen corrupta.')
