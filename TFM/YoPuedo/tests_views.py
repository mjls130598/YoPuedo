from django.test import TestCase
from TFM.settings import BASE_DIR


# Comprobamos el funcionamiento de la URL registrarse
class RegistroViewTest(TestCase):
    def test_url_accesible(self):
        resp = self.client.get('/registrarse/')
        self.assertEqual(resp.status_code, 200)

    def test_post_registro(self):
        data = {
            'email': "mariajesus@gmail.com",
            'nombre': "María Jesús",
            'password': 'Password1.',
            'password_again': 'Password1.',
            'foto_de_perfil': f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        }
        resp = self.client.post('/registrarse/', data)
        self.assertEqual(resp.status_code, 200)
