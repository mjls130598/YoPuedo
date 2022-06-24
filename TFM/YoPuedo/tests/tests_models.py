from django.test import TestCase
from TFM.YoPuedo.models import Usuario
from TFM.settings import BASE_DIR


# Comprobamos el funcionamiento de la tabla USUARIO
class UsuarioModelTest(TestCase):
    def setUpTestData(cls):
        Usuario.objects.create(email="mariajesus@gmail.com", nombre="María Jesús",
                               password="Password1.",
                               fotoPerfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

    def test_email(self):
        usuario = Usuario.objects.get(email="mariajesus@gmail.com")
        self.assertEqual(usuario.email, 'mariajesus@gmail.com')

    def test_nombre(self):
        usuario = Usuario.objects.get(email="mariajesus@gmail.com")
        self.assertEqual(usuario.nombre, 'María Jesús')

    def test_password(self):
        usuario = Usuario.objects.get(email="mariajesus@gmail.com")
        self.assertEqual(usuario.password, 'Password1.')

    def test_foto_perfil(self):
        usuario = Usuario.objects.get(email="mariajesus@gmail.com")
        self.assertEqual(usuario.fotoPerfil, f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")