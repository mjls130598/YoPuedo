from django.test import TestCase
from TFM.settings import BASE_DIR
from http import HTTPStatus
from ..models import Usuario


# Comprobamos el funcionamiento de la URL registrarse
class RegistroViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create(email="mj@gmail.com", nombre="María Jesús",
                               password="Password1.",
                               fotoPerfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg",
                               claveFija="clavefija",
                               claveAleatoria="clavefija")

    def test_url_accesible(self):
        resp = self.client.get('/registrarse/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_post_registro(self):
        data = {
            'email': "mariajesus@gmail.com",
            'nombre': "María Jesús",
            'password': 'Password1.',
            'password_again': 'Password1.',
            'foto_de_perfil': f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        }
        resp = self.client.post('/registrarse/', data)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_validar_clave(self):
        data = {
            'email': "mj@gmail.com",
            'contador': 0,
            'tipo': 'registro',
            'clave': 'clavefija'
        }

        resp = self.client.post('/validar_clave/', data)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_validar_clave_incorrecta(self):
        data = {
            'email': "mj@gmail.com",
            'contador': 0,
            'tipo': 'registro',
            'clave': 'clave'
        }

        resp = self.client.post('/validar_clave/', data)
        self.assertEqual(resp.path, '/validar_clave/')
