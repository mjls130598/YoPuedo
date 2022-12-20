from django.contrib.auth import login
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from TFM.settings import BASE_DIR
from http import HTTPStatus
from django.test.client import Client

from ..models import Usuario, Reto, Etapa, Animador, Participante


##########################################################################################

# Comprobamos el funcionamiento de la URL registrarse
class RegistroViewTest(TestCase):

    def test_url_accesible(self):
        resp = self.client.get('/registrarse/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_post_registro(self):
        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        data = {
            'email': "registro@email.com",
            'nombre': "María Jesús",
            'password': 'Password1.',
            'password_again': 'Password1.',
            'foto_de_perfil': SimpleUploadedFile(foto_perfil.name, foto_perfil.read())
        }
        resp = self.client.post('/registrarse/', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.CREATED)
        self.assertTrue(Usuario.objects.filter(email='registro@email.com').exists())


##########################################################################################

# Comprobamos el funcionamiento de la URL validar clave
class ClaveViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create_user(email="clave_view@gmail.com", nombre="María Jesús",
                                    password="Password1.", clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

    def test_url_registro_accesible(self):
        resp = self.client.get('/validar_clave/registro/clave_view@gmail.com')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_url_inicio_accesible(self):
        resp = self.client.get('/validar_clave/inicio_sesion/clave_view@gmail.com')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_post_registro_correcto(self):
        data = {
            'email': 'clave_view@gmail.com',
            'contador': 0,
            'clave': 'clavealeat'
        }

        resp = self.client.post('/validar_clave/registro/clave_view@gmail.com', data)
        self.assertEqual(resp.status_code, HTTPStatus.ACCEPTED)
        user = Usuario.objects.get(email='clave_view@gmail.com')
        self.assertTrue(user.is_authenticated)

    def test_post_inicio_correcto(self):
        data = {
            'email': 'clave_view@gmail.com',
            'contador': 0,
            'clave': 'clavealeat'
        }

        resp = self.client.post('/validar_clave/inicio_sesion/clave_view@gmail.com', data)
        self.assertEqual(resp.status_code, HTTPStatus.ACCEPTED)
        user = Usuario.objects.get(email='clave_view@gmail.com')
        self.assertTrue(user.is_authenticated)

    def test_post_inicio_incorrecto(self):
        data = {
            'email': 'clave_view@gmail.com',
            'contador': 2,
            'clave': 'clavealeatoria'
        }

        resp = self.client.post('/validar_clave/inicio_sesion/clave_view@gmail.com', data)
        self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(Usuario.objects.filter(email='clave_view@gmail.com').exists())

    def test_post_registro_incorrecto(self):
        data = {
            'email': 'clave_view@gmail.com',
            'contador': 2,
            'clave': 'clavealeatoria'
        }

        resp = self.client.post('/validar_clave/registro/clave_view@gmail.com', data)
        self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(not Usuario.objects.filter(email='clave_view@gmail.com').exists())


##########################################################################################

# Comprobamos el funcionamiento de la URL iniciar sesión
class InicioViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create_user(email="inicio_view@gmail.com", nombre="María Jesús",
                                    password="Password1.", clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

    def test_url_accesible(self):
        resp = self.client.get('/iniciar_sesion/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_post_inicio(self):
        data = {
            'email_sesion': "inicio_view@gmail.com",
            'password_sesion': 'Password1.',
        }
        resp = self.client.post('/iniciar_sesion/', data)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)


##########################################################################################

# Comprobamos el funcionamiento de la URL mis retos
class MisRetosViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        usuario = Usuario.objects.create_user(email="misretos_view@gmail.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")


        client = Client()
        client.login(username='misretos_view@gmail.com', password="Password1.")

    def test_url_accesible(self):
        resp = self.client.get('/mis_retos/')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)

    def test_url_tipo_accesible(self):
        resp = self.client.get('/mis_retos/?tipo=individuales')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)

    def test_url_categoria_accesible(self):
        resp = self.client.get('/mis_retos/?tipo=individuales&categoria=economia')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)


##########################################################################################

# Comprobamos el funcionamiento de la URL nuevo reto
class NuevoRetoTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create_user(email="nuevoreto_view@gmail.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        Usuario.objects.create_user(email="animador_view@gmail.com",
                                    nombre="María Jesús",
                                    password="Password1.",
                                    clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        Usuario.objects.create_user(email="participante_view@gmail.com",
                                    nombre="María Jesús",
                                    password="Password1.",
                                    clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        client = Client()
        client.login(username='nuevoreto_view@gmail.com', password="Password1.")

    def test_url_accesible(self):
        resp = self.client.get('/nuevo_reto/')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)

    def test_url_tipo_accesible(self):
        resp = self.client.get('/nuevo_reto/?tipo=individual')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)

    def test_post_reto_individual(self):

        data = {
            # General
            'titulo': 'Prueba RETO VIEWS',
            'objetivo_imagen': '',
            'objetivo_audio': '',
            'objetivo_video': '',
            'objetivo_texto': 'Objetivo RETO VIEWS',
            'recompensa_imagen': '',
            'recompensa_audio': '',
            'recompensa_video': '',
            'categoria': 'economia',

            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '1',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': 'Objetivo ETAPA VIEWS',
        }

        usuario = Usuario.objects.get(email="nuevoreto_view@gmail.com")

        resp = self.client.post('/nuevo_reto/?tipo=individual', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue("/mis_retos/" in resp.url)
        id_reto = resp.url[-50:]
        self.assertTrue(Reto.objects.filter(id_reto=id_reto).exists())
        self.assertTrue(Etapa.objects.filter(id_reto=id_reto).exists())
        self.assertEqual(Participante.objects.filter(id_reto=id_reto).last().usuario,
                         usuario)

    def test_post_reto_individual_animadores(self):

        data = {
            # General
            'titulo': 'Prueba RETO VIEWS',
            'objetivo_imagen': '',
            'objetivo_audio': '',
            'objetivo_video': '',
            'objetivo_texto': 'Objetivo RETO VIEWS',
            'recompensa_imagen': '',
            'recompensa_audio': '',
            'recompensa_video': '',
            'categoria': 'economia',

            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '1',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': 'Objetivo ETAPA VIEWS',

            # Animadores
            'animador': ["animador_view@gmail.com"],
            'superanimador-animador_view@gmail.com': 'false'
        }

        usuario = Usuario.objects.get(email="nuevoreto_view@gmail.com")

        resp = self.client.post('/nuevo_reto/?tipo=individual', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue("/mis_retos/" in resp.url)
        id_reto = resp.url[-50:]
        self.assertTrue(Reto.objects.filter(id_reto=id_reto).exists())
        self.assertTrue(Etapa.objects.filter(id_reto=id_reto).exists())
        self.assertEqual(Participante.objects.filter(id_reto=id_reto).last().usuario,
                         usuario)
        self.assertTrue(Animador.objects.filter(id_reto=id_reto).exists())

    def test_post_reto_colectivo(self):

        data = {
            # General
            'titulo': 'Prueba RETO VIEWS',
            'objetivo_imagen': '',
            'objetivo_audio': '',
            'objetivo_video': '',
            'objetivo_texto': 'Objetivo RETO VIEWS',
            'recompensa_imagen': '',
            'recompensa_audio': '',
            'recompensa_video': '',
            'categoria': 'economia',

            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '1',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': 'Objetivo ETAPA VIEWS',

            # Animadores
            'animador': ["animador_view@gmail.com"],
            'superanimador-animador_view@gmail.com': 'false',

            # Participantes
            'participante': ["participante_view@gmail.com"]
        }

        usuario = Usuario.objects.get(email="nuevoreto_view@gmail.com")

        resp = self.client.post('/nuevo_reto/?tipo=colectivo', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue("/mis_retos/" in resp.url)
        id_reto = resp.url[-50:]
        self.assertTrue(Reto.objects.filter(id_reto=id_reto).exists())
        self.assertTrue(Etapa.objects.filter(id_reto=id_reto).exists())
        self.assertEqual(Participante.objects.filter(id_reto=id_reto).last().usuario,
                         usuario)
        self.assertTrue(Animador.objects.filter(id_reto=id_reto).exists())
        self.assertTrue(Participante.objects.filter(id_reto=id_reto).exists())
