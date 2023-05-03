import json

from django.contrib import auth
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from TFM.settings import BASE_DIR
from http import HTTPStatus
from django.test.client import Client

from ..models import Usuario, Reto, Etapa, Animador, Participante, Amistad, Notificacion
from ..utils import Utils


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
            'email': "registro@yopuedo.com",
            'nombre': "María Jesús",
            'password': 'Password1.',
            'password_again': 'Password1.',
            'foto_de_perfil': SimpleUploadedFile(foto_perfil.name, foto_perfil.read())
        }
        resp = self.client.post('/registrarse/', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.CREATED)
        self.assertTrue(Usuario.objects.filter(email='registro@yopuedo.com').exists())


##########################################################################################

# Comprobamos el funcionamiento de la URL validar clave
class ClaveViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create_user(email="clave_view@yopuedo.com", nombre="María Jesús",
                                    password="Password1.", clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

    def test_url_registro_accesible(self):
        resp = self.client.get('/validar_clave/registro/clave_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_url_inicio_accesible(self):
        resp = self.client.get('/validar_clave/inicio_sesion/clave_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_url_eliminar_accesible(self):
        self.client.login(username='clave_view@yopuedo.com', password="Password1.")
        resp = self.client.get('/validar_clave/eliminar/clave_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_post_registro_correcto(self):
        data = {
            'email': 'clave_view@yopuedo.com',
            'contador': 0,
            'clave': 'clavealeat'
        }

        resp = self.client.post('/validar_clave/registro/clave_view@yopuedo.com', data)
        self.assertEqual(resp.status_code, HTTPStatus.ACCEPTED)
        user = Usuario.objects.get(email='clave_view@yopuedo.com')
        self.assertTrue(user.is_authenticated)

    def test_post_inicio_correcto(self):
        data = {
            'email': 'clave_view@yopuedo.com',
            'contador': 0,
            'clave': 'clavealeat'
        }

        resp = self.client.post('/validar_clave/inicio_sesion/clave_view@yopuedo.com',
                                data)
        self.assertEqual(resp.status_code, HTTPStatus.ACCEPTED)
        user = Usuario.objects.get(email='clave_view@yopuedo.com')
        self.assertTrue(user.is_authenticated)

    def test_post_eliminar_incorrecto(self):
        data = {
            'email': 'clave_view@yopuedo.com',
            'contador': 2,
            'clave': 'clavealeatoria'
        }

        resp = self.client.post('/validar_clave/eliminar/clave_view@yopuedo.com', data)
        self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(Usuario.objects.filter(email='clave_view@yopuedo.com').exists())

    def test_post_inicio_incorrecto(self):
        data = {
            'email': 'clave_view@yopuedo.com',
            'contador': 2,
            'clave': 'clavealeatoria'
        }

        resp = self.client.post('/validar_clave/inicio_sesion/clave_view@yopuedo.com',
                                data)
        self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)
        self.assertTrue(Usuario.objects.filter(email='clave_view@yopuedo.com').exists())

    def test_post_registro_incorrecto(self):
        data = {
            'email': 'clave_view@yopuedo.com',
            'contador': 2,
            'clave': 'clavealeatoria'
        }

        resp = self.client.post('/validar_clave/registro/clave_view@yopuedo.com', data)
        self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)
        self.assertFalse(Usuario.objects.filter(email='clave_view@yopuedo.com').exists())

    def test_post_eliminar_correcto(self):
        Usuario.objects.create_user(email="clave_view@yopuedo.com", nombre="María Jesús",
                                    password="Password1.", clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        self.client.login(username='clave_view@yopuedo.com', password="Password1.")

        data = {
            'email': 'clave_view@yopuedo.com',
            'contador': 0,
            'clave': 'clavealeat'
        }

        resp = self.client.post('/validar_clave/eliminar/clave_view@yopuedo.com', data)
        self.assertEqual(resp.status_code, HTTPStatus.ACCEPTED)
        self.assertFalse(Usuario.objects.filter(email='clave_view@yopuedo.com').exists())


##########################################################################################

# Comprobamos el funcionamiento de la URL iniciar sesión
class InicioViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create_user(email="inicio_view@yopuedo.com", nombre="María Jesús",
                                    password="Password1.", clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

    def test_url_accesible(self):
        resp = self.client.get('/iniciar_sesion/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_post_inicio(self):
        data = {
            'email_sesion': "inicio_view@yopuedo.com",
            'password_sesion': 'Password1.',
        }
        resp = self.client.post('/iniciar_sesion/', data)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)


##########################################################################################

# Comprobamos el funcionamiento de la URL mis retos
class MisRetosViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create_user(email="misretos_view@yopuedo.com",
                                    nombre="María Jesús", password="Password1.",
                                    clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        client = Client()
        client.login(username='misretos_view@yopuedo.com', password="Password1.")

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

# Comprobamos el funcionamiento de la URL obtener retos de un estado
class GetRetosTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Creamos usuarios
        usuario = Usuario.objects.create_user(email="getretos_view@yopuedo.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        otro_usuario = Usuario.objects.create_user(email="getretos_otro_view@yopuedo.com",
                                                   nombre="María Jesús",
                                                   password="Password1.",
                                                   clave_aleatoria="clavealeat",
                                                   clave_fija="clavefijausuario",
                                                   foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        # Creamos el primer reto
        reto = Reto(id_reto=Utils.crear_id_reto(), titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS", categoria="inteligencia",
                    recompensa="RECOMPENSA RETO VIEWS", coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

        # Creamos el animador del reto
        animador = Animador()
        animador.save()
        animador.reto = reto
        animador.usuario = otro_usuario
        animador.superanimador = True
        animador.save()

        # Creamos el segundo reto
        reto2 = Reto(id_reto=Utils.crear_id_reto(), titulo="PRUEBA RETO 2 VIEWS",
                     objetivo="OBJETIVO RETO VIEWS", categoria="economia",
                     recompensa="RECOMPENSA RETO VIEWS", coordinador=usuario,
                     estado="Finalizado")
        reto2.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO 2 VIEWS",
              reto=reto2).save()

        # Creamos participantes en el reto
        participante = Participante()
        participante.save()
        participante.reto = reto2
        participante.usuario = otro_usuario

    def get_propuesto_individual(self):
        # Logueamos el primer usuario
        self.client.login(username='getretos_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=individuales&estado=propuesto')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 1)

    def get_propuesto_colectivo(self):
        # Logueamos el primer usuario
        self.client.login(username='getretos_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=colectivos&estado=propuesto')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 0)

    def get_animando_individual(self):
        # Logueamos el segundo usuario
        self.client.login(username='getretos_otro_view@yopuedo.com',
                          password="Password1.")

        resp = self.client.get('/retos/?tipo=individuales&estado=animando')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 1)

    def get_animando_colectivo(self):
        # Logueamos el segundo usuario
        self.client.login(username='getretos_otro_view@yopuedo.com',
                          password="Password1.")

        resp = self.client.get('/retos/?tipo=colectivos&estado=animando')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 0)

    def get_finalizado_individual(self):
        # Logueamos el segundo usuario
        self.client.login(username='getretos_otro_view@yopuedo.com',
                          password="Password1.")

        resp = self.client.get('/retos/?tipo=individuales&estado=finalizados')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 0)

    def get_finalizado_colectivos(self):
        # Logueamos el segundo usuario
        self.client.login(username='getretos_otro_view@yopuedo.com',
                          password="Password1.")

        resp = self.client.get('/retos/?tipo=colectivos&estado=finalizados')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 1)

    def get_proceso_individual(self):
        # Logueamos el primer usuario
        self.client.login(username='getretos_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=individuales&estado=proceso')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 0)

    def get_proceso_colectivos(self):
        # Logueamos el primer usuario
        self.client.login(username='getretos_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=colectivos&estado=proceso')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 0)

    def get_categoria_individual(self):
        # Logueamos el primer usuario
        self.client.login(username='getretos_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=individuales&categoria=inteligencia&estado'
                               '=propuesto')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 1)

    def get_no_categoria_colectivo(self):
        # Logueamos el primer usuario
        self.client.login(username='getretos_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=colectivos&categoria=inteligencia&estado'
                               '=propuesto')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 0)


##########################################################################################

# Comprobamos el funcionamiento de la URL nuevo reto
class NuevoRetoTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        usuario = Usuario.objects.create_user(email="nuevoreto_view@yopuedo.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        Usuario.objects.create_user(email="animador_view@yopuedo.com",
                                    nombre="María Jesús",
                                    password="Password1.",
                                    clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        Usuario.objects.create_user(email="participante_view@yopuedo.com",
                                    nombre="María Jesús",
                                    password="Password1.",
                                    clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")
        cls.client = Client()
        cls.user = usuario

    def test_url_accesible(self):
        self.client.login(username='nuevoreto_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/nuevo_reto/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_url_tipo_accesible(self):
        self.client.login(username='nuevoreto_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/nuevo_reto/?tipo=individual')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_post_reto_individual(self):
        self.client.login(username='nuevoreto_view@yopuedo.com', password="Password1.")

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
            'recompensa_texto': 'Recompensa RETO VIEWS',
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

        resp = self.client.post('/nuevo_reto/?tipo=individual', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        print("URL" + resp.url)
        self.assertTrue("/reto/" in resp.url)
        id_reto = resp.url[-50:]
        self.assertTrue(Reto.objects.filter(id_reto=id_reto).exists())
        self.assertTrue(Etapa.objects.filter(reto__id_reto=id_reto).exists())
        self.assertEqual(len(Participante.objects.filter(reto__id_reto=id_reto).all()), 1)

    def test_post_reto_individual_animadores(self):
        self.client.login(username='nuevoreto_view@yopuedo.com', password="Password1.")

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
            'recompensa_texto': 'Recompensa RETO VIEWS',
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
            'animador': ["animador_view@yopuedo.com"],
            'superanimador-animador_view@yopuedo.com': 'false'
        }

        resp = self.client.post('/nuevo_reto/?tipo=individual', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue("/reto/" in resp.url)
        id_reto = resp.url[-50:]
        self.assertTrue(Reto.objects.filter(id_reto=id_reto).exists())
        self.assertTrue(Etapa.objects.filter(reto__id_reto=id_reto).exists())
        self.assertEqual(len(Participante.objects.filter(reto__id_reto=id_reto).all()), 1)
        self.assertTrue(Animador.objects.filter(reto__id_reto=id_reto).exists())
        self.assertTrue(Notificacion.objects.filter(
            usuario__email="animador_view@yopuedo.com").exists())

    def test_post_reto_colectivo(self):
        self.client.login(username='nuevoreto_view@yopuedo.com', password="Password1.")

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
            'recompensa_texto': 'Recompensa RETO VIEWS',
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
            'animador': ["animador_view@yopuedo.com"],
            'superanimador-animador_view@yopuedo.com': 'false',

            # Participantes
            'participante': ["participante_view@yopuedo.com"]
        }

        resp = self.client.post('/nuevo_reto/?tipo=colectivo', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue("/reto/" in resp.url)
        id_reto = resp.url[-50:]
        self.assertTrue(Reto.objects.filter(id_reto=id_reto).exists())
        self.assertTrue(Etapa.objects.filter(reto__id_reto=id_reto).exists())
        self.assertTrue(Animador.objects.filter(reto__id_reto=id_reto).exists())
        self.assertTrue(Notificacion.objects.filter(
            usuario__email="animador_view@yopuedo.com").exists())
        self.assertTrue(len(Participante.objects.filter(reto__id_reto=id_reto).all()) > 1)
        self.assertTrue(Notificacion.objects.filter(
            usuario__email="participante_view@yopuedo.com").exists())


##########################################################################################

# Comprobamos el funcionamiento de la URL obtener amistades
class GetAmigosTest(TestCase):
    def setUpTestData(cls):
        usuario = Usuario.objects.create_user(email="amigo_view@yopuedo.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        usuario2 = Usuario.objects.create_user(email="amigo2_view@yopuedo.com",
                                               nombre="María Jesús",
                                               password="Password1.",
                                               clave_aleatoria="clavealeat",
                                               clave_fija="clavefijausuario",
                                               foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        amistad = Amistad()
        amistad.save()
        amistad.amigo = usuario
        amistad.otro_amigo = usuario2
        amistad.save()

    def get_amigo(self):
        self.client.login(username='amigo_view@yopuedo.com', password='Password1.')
        resp = self.client.get('/amigos/')
        self.assertEqual(len(resp.context['amigos']), 1)
        self.assertEqual(resp.status_code, HTTPStatus.OK)


##########################################################################################

# Comprobamos el funcionamiento de la URL obtener reto
class GetRetoTest(TestCase):
    def setUpTestData(cls):
        # Creamos usuarios
        usuario = Usuario.objects.create_user(email="getreto_view@yopuedo.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        Usuario.objects.create_user(email="otro_view@yopuedo.com",
                                    nombre="María Jesús",
                                    password="Password1.",
                                    clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        # Creamos el primer reto
        reto = Reto(id_reto=Utils.crear_id_reto(), titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS", categoria="inteligencia",
                    recompensa="RECOMPENSA RETO VIEWS", coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

    def permitida_obtencion(self):
        self.client.login(username="getreto_view@yopuedo.com", password='Password1.')
        reto = Reto.objects.filter(coordinador__email='getreto_view@yopuedo.com').first()
        resp = self.client.get(f'/reto/{reto.id_reto}')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)

    def no_permitida_obtencion(self):
        self.client.login(username="otro_view@yopuedo.com", password='Password1.')
        reto = Reto.objects.filter(coordinador__email='getreto_view@yopuedo.com').first()
        resp = self.client.get(f'/reto/{reto.id_reto}')
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)


##########################################################################################

# Comprobamos el funcionamiento de la URL iniciar reto
class IniciarRetoTest(TestCase):
    def setUpTestData(cls):
        # Creamos usuarios
        usuario = Usuario.objects.create_user(email="iniciarreto_view@yopuedo.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        otro_usuario = Usuario.objects.create_user(
            email="iniciarreto_otro_view@yopuedo.com",
            nombre="María Jesús",
            password="Password1.",
            clave_aleatoria="clavealeat",
            clave_fija="clavefijausuario",
            foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        # Creamos el primer reto
        reto = Reto(id_reto=Utils.crear_id_reto(), titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS", categoria="inteligencia",
                    recompensa="RECOMPENSA RETO VIEWS", coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

        # Creamos el animador del reto
        animador = Animador()
        animador.save()
        animador.reto = reto
        animador.usuario = otro_usuario
        animador.superanimador = True
        animador.save()

    def permitida_obtencion(self):
        self.client.login(username="iniciarreto_view@yopuedo.com", password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='iniciarreto_view@yopuedo.com').first()
        resp = self.client.get(f'/iniciar_reto/{reto.id_reto}')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        reto = Reto.objects.filter(
            coordinador__email='iniciarreto_view@yopuedo.com').first()

        self.assertEqual(reto.estado, "En proceso")
        self.assertEqual(reto.etapa_set.first().estado, "En proceso")

    def no_permitida_obtencion(self):
        self.client.login(username="iniciarreto_otro_view@yopuedo.com",
                          password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='iniciarreto_view@yopuedo.com').first()
        resp = self.client.get(f'/iniciar_reto/{reto.id_reto}')
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)


##########################################################################################

# Comprobamos el funcionamiento de la URL eliminar reto
class EliminarRetoTest(TestCase):
    def setUpTestData(cls):
        # Creamos usuarios
        usuario = Usuario.objects.create_user(email="eliminarreto_view@yopuedo.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        otro_usuario = Usuario.objects.create_user(
            email="eliminarreto_otro_view@yopuedo.com",
            nombre="María Jesús",
            password="Password1.",
            clave_aleatoria="clavealeat",
            clave_fija="clavefijausuario",
            foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        # Creamos el primer reto
        reto = Reto(id_reto=Utils.crear_id_reto(), titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS", categoria="inteligencia",
                    recompensa="RECOMPENSA RETO VIEWS", coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

        # Creamos el animador del reto
        animador = Animador()
        animador.save()
        animador.reto = reto
        animador.usuario = otro_usuario
        animador.superanimador = True
        animador.save()

    def permitida_obtencion(self):
        self.client.login(username="eliminarreto_view@yopuedo.com", password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='eliminarreto_view@yopuedo.com').first()
        resp = self.client.get(f'/eliminar_reto/{reto.id_reto}')

        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertFalse(Reto.objects.filter(id_reto=reto.id_reto).exists())
        self.assertFalse(Etapa.objects.filter(reto__id_reto=reto.id_reto).exists())
        self.assertFalse(Animador.objects.filter(reto__id_reto=reto.id_reto).exists())

    def no_permitida_obtencion(self):
        self.client.login(username="eliminarreto_otro_view@yopuedo.com",
                          password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='eliminarreto_view@yopuedo.com').first()
        resp = self.client.get(f'/eliminar_reto/{reto.id_reto}')
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)


##########################################################################################

# Comprobamos el funcionamiento de la URL cambiar coordinador del reto
class CoordinadorRetoTest(TestCase):
    def setUpTestData(cls):
        # Creamos usuarios
        usuario = Usuario.objects.create_user(email="coordinadorreto_view@yopuedo.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        otro_usuario = Usuario.objects.create_user(
            email="coordinadorreto_otro_view@yopuedo.com",
            nombre="María Jesús",
            password="Password1.",
            clave_aleatoria="clavealeat",
            clave_fija="clavefijausuario",
            foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        # Creamos el primer reto
        reto = Reto(id_reto=Utils.crear_id_reto(), titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS", categoria="inteligencia",
                    recompensa="RECOMPENSA RETO VIEWS", coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

        # Creamos el participante del reto
        participante = Participante()
        participante.save()
        participante.reto = reto
        participante.usuario = otro_usuario
        participante.save()

    def no_permitida_obtencion(self):
        self.client.login(username="coordinadorreto_otro_view@yopuedo.com",
                          password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='coordinadorreto_view@yopuedo.com').first()
        resp = self.client.post(f'/coordinador_reto/{reto.id_reto}')
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    def permitida_obtencion(self):
        self.client.login(username="coordinadorreto_view@yopuedo.com",
                          password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='coordinadorreto_view@yopuedo.com').first()

        resp = self.client.get(f'/coordinador_reto/{reto.id_reto}')

        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertEqual(len(resp.context['participantes']), 1)

    def permitida_obtencion_consulta(self):
        self.client.login(username="coordinadorreto_view@yopuedo.com",
                          password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='coordinadorreto_view@yopuedo.com').first()

        data = {
            'consulta': 'María'
        }

        resp = self.client.get(f'/coordinador_reto/{reto.id_reto}', data)

        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertEqual(len(resp.context['participantes']), 1)

    def permitido_cambio(self):
        self.client.login(username="coordinadorreto_view@yopuedo.com",
                          password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='coordinadorreto_view@yopuedo.com').first()
        data = {
            'coordinador': 'coordinadorreto_otro_view@yopuedo.com'
        }

        resp = self.client.post(f'/coordinador_reto/{reto.id_reto}', data)

        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        reto = Reto.objects.get(id_reto=reto.id_reto)
        self.assertEqual(reto.coordinador.email, 'coordinadorreto_otro_view@yopuedo.com')


##########################################################################################

# Comprobamos el funcionamiento de la URL eliminar reto
class EliminarAnimadorRetoTest(TestCase):
    def setUpTestData(cls):
        # Creamos usuarios
        usuario = Usuario.objects.create_user(
            email="eliminaranimadorreto_view@yopuedo.com",
            nombre="María Jesús", password="Password1.",
            clave_aleatoria="clavealeat",
            clave_fija="clavefijausuario",
            foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        otro_usuario = Usuario.objects.create_user(
            email="eliminaranimadorreto_otro_view@yopuedo.com",
            nombre="María Jesús",
            password="Password1.",
            clave_aleatoria="clavealeat",
            clave_fija="clavefijausuario",
            foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        # Creamos el primer reto
        reto = Reto(id_reto=Utils.crear_id_reto(), titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS", categoria="inteligencia",
                    recompensa="RECOMPENSA RETO VIEWS", coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

        # Creamos el animador del reto
        animador = Animador()
        animador.save()
        animador.reto = reto
        animador.usuario = otro_usuario
        animador.superanimador = True
        animador.save()

    def permitida_obtencion(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='eliminaranimadorreto_view@yopuedo.com').first()
        resp = self.client.get(f'/animador_reto/{reto.id_reto}')

        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertFalse(Animador.objects.filter(reto__id_reto=reto.id_reto,
                                                 usuario__email="eliminaranimadorreto_otro_view@yopuedo.com").exists())

    def no_permitida_obtencion(self):
        self.client.login(username="eliminaranimadorreto_view@yopuedo.com",
                          password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='eliminaranimadorreto_view@yopuedo.com').first()
        resp = self.client.get(f'/animador_reto/{reto.id_reto}')
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)


##########################################################################################
# Comprobamos el funcionamiento de editar reto
class EditarRetoTest(TestCase):
    def setUpTestData(cls):
        # Creamos usuarios
        Usuario.objects.create_user(email="editarreto_view@yopuedo.com",
                                    nombre="María Jesús", password="Password1.",
                                    clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        # Creamos usuarios
        Usuario.objects.create_user(email="extrañoeditando_view@yopuedo.com",
                                    nombre="María Jesús", password="Password1.",
                                    clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

    def objetivoRetoMedia(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@yopuedo"
                             f".com"
                             f".jpg",
                    categoria="inteligencia",
                    recompensa="RECOMPENSA RETO VIEWS", coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

        data = {
            # General
            'titulo': 'Prueba RETO VIEWS',
            'objetivo_imagen': '',
            'objetivo_audio': '',
            'objetivo_video': '',
            'objetivo_texto': '',
            'recompensa_imagen': '',
            'recompensa_audio': '',
            'recompensa_video': '',
            'recompensa_texto': 'Recompensa RETO VIEWS',
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

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertTrue(f"/reto/{id_reto}" in resp.url)
        self.assertEqual(reto.objetivo,
                         f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com"
                         f".jpg")

    def objetivoRetoVacio(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo=f"OBJETIVO RETO VIEWS",
                    categoria="inteligencia",
                    recompensa="RECOMPENSA RETO VIEWS", coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

        data = {
            # General
            'titulo': 'Prueba RETO VIEWS',
            'objetivo_imagen': '',
            'objetivo_audio': '',
            'objetivo_video': '',
            'objetivo_texto': '',
            'recompensa_imagen': '',
            'recompensa_audio': '',
            'recompensa_video': '',
            'recompensa_texto': 'Recompensa RETO VIEWS',
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

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertTrue(f"/editar_reto/{id_reto}" in resp.url)
        self.assertEqual(reto.objetivo, "OBJETIVO RETO VIEWS")

    def objetivoRetoNuevo(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@yopuedo"
                             f".com"
                             f".jpg",
                    categoria="inteligencia",
                    recompensa="RECOMPENSA RETO VIEWS", coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

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
            'recompensa_texto': 'Recompensa RETO VIEWS',
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

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertTrue(f"/reto/{id_reto}" in resp.url)
        self.assertEqual(reto.objetivo, "Objetivo RETO VIEWS")

    def recompensaRetoMedia(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS",
                    categoria="inteligencia",
                    recompensa=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariaje"
                               f"sus@yopuedo.com.jpg",
                    coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

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
            'recompensa_texto': '',
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

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertTrue(f"/reto/{id_reto}" in resp.url)
        self.assertEqual(reto.recompensa,
                         f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com"
                         f".jpg")

    def recompensaRetoVacia(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS",
                    categoria="inteligencia",
                    recompensa="RECOMPENSA RETO VIEWS",
                    coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

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
            'recompensa_texto': '',
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

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertTrue(f"/editar_reto/{id_reto}" in resp.url)
        self.assertEqual(reto.recompensa, "RECOMPENSA RETO VIEWS")

    def recompensaRetoNuevo(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS",
                    categoria="inteligencia",
                    recompensa=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@yopuedo"
                               f".com"
                               f".jpg",
                    coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

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
            'recompensa_texto': 'Recompensa RETO VIEWS',
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

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertTrue(f"/reto/{id_reto}" in resp.url)
        self.assertEqual(reto.recompensa, "Recompensa RETO VIEWS")

    def objetivoEtapaMedia(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS",
                    categoria="inteligencia",
                    recompensa="RECOMPENSA RETO VIEWS",
                    coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        id_etapa = Utils.crear_id_etapa(0)
        Etapa(id_etapa=id_etapa,
              objetivo=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg",
              reto=reto).save()

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
            'recompensa_texto': '',
            'categoria': 'economia',

            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '1',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-id_etapa': id_etapa,
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': '',
        }

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertTrue(f"/reto/{id_reto}" in resp.url)
        self.assertEqual(reto.etapa_set.all().first().objetivo,
                         f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com"
                         f".jpg")

    def objetivoEtapaVacia(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS",
                    categoria="inteligencia",
                    recompensa="RECOMPENSA RETO VIEWS",
                    coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        id_etapa = Utils.crear_id_etapa(0)
        Etapa(id_etapa=id_etapa,
              objetivo="OBJETIVO ETAPA VIEWS",
              reto=reto).save()

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
            'recompensa_texto': '',
            'categoria': 'economia',

            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '1',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-id_etapa': id_etapa,
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': '',
        }

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertTrue(f"/editar_reto/{id_reto}" in resp.url)
        self.assertEqual(reto.etapa_set.all().first().objetivo, "OBJETIVO ETAPA VIEWS")

    def objetivoEtapaNuevo(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS",
                    categoria="inteligencia",
                    recompensa=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@yopuedo"
                               f".com"
                               f".jpg",
                    coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        id_etapa = Utils.crear_id_etapa(0)
        Etapa(id_etapa=id_etapa,
              objetivo=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg",
              reto=reto).save()

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
            'recompensa_texto': 'Recompensa RETO VIEWS',
            'categoria': 'economia',

            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '1',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-id_etapa': id_etapa,
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': 'Objetivo ETAPA VIEWS',
        }

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertTrue(f"/reto/{id_reto}" in resp.url)
        self.assertEqual(reto.etapa_set.all().first().objetivo, "Objetivo ETAPA VIEWS")

    def etapaNuevaVacia(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS",
                    categoria="inteligencia",
                    recompensa=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@yopuedo"
                               f".com"
                               f".jpg",
                    coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        id_etapa = Utils.crear_id_etapa(0)
        Etapa(id_etapa=id_etapa,
              objetivo=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg",
              reto=reto).save()

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
            'recompensa_texto': 'Recompensa RETO VIEWS',
            'categoria': 'economia',

            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '2',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-id_etapa': id_etapa,
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': 'Objetivo ETAPA VIEWS',

            # Nueva Etapa
            'form-0-id_etapa': '',
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': '',
        }

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertTrue(f"/editar_reto/{id_reto}" in resp.url)
        self.assertEqual(len(reto.etapa_set.all()), 1)

    def etapaNueva(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS",
                    categoria="inteligencia",
                    recompensa=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@yopuedo"
                               f".com"
                               f".jpg",
                    coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        id_etapa = Utils.crear_id_etapa(0)
        Etapa(id_etapa=id_etapa,
              objetivo=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg",
              reto=reto).save()

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
            'recompensa_texto': 'Recompensa RETO VIEWS',
            'categoria': 'economia',

            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '2',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-id_etapa': id_etapa,
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': 'Objetivo ETAPA VIEWS',

            # Nueva Etapa
            'form-0-id_etapa': '',
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': 'Objetivo NUEVO Etapa VIEWS',
        }

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertTrue(f"/editar_reto/{id_reto}" in resp.url)
        self.assertEqual(len(reto.etapa_set.all()), 2)
        self.assertEqual(reto.etapa_set.all().last().objetivo,
                         "Objetivo NUEVO Etapa VIEWS")

    def retoComenzado(self):
        self.client.login(username="eliminaranimadorreto_otro_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS",
                    categoria="inteligencia",
                    recompensa=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@yopuedo"
                               f".com"
                               f".jpg",
                    coordinador=usuario, estado="En proceso")
        reto.save()

        # Creamos la primera etapa del reto
        id_etapa = Utils.crear_id_etapa(0)
        Etapa(id_etapa=id_etapa,
              objetivo=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg",
              reto=reto, estado="En proceso").save()

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
            'recompensa_texto': 'Recompensa RETO VIEWS',
            'categoria': 'economia',

            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '2',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-id_etapa': id_etapa,
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': 'Objetivo ETAPA VIEWS',

            # Nueva Etapa
            'form-0-id_etapa': '',
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': 'Objetivo NUEVO Etapa VIEWS',
        }

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)

    def extrañoEditando(self):
        self.client.login(username="extrañoeditando_view@yopuedo.com",
                          password='Password1.')

        usuario = Usuario.objects.get(email="editarreto_view@yopuedo.com")
        id_reto = Utils.crear_id_reto()

        # Creamos el reto
        reto = Reto(id_reto=id_reto,
                    titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS",
                    categoria="inteligencia",
                    recompensa=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@yopuedo"
                               f".com"
                               f".jpg",
                    coordinador=usuario)
        reto.save()

        # Creamos la primera etapa del reto
        id_etapa = Utils.crear_id_etapa(0)
        Etapa(id_etapa=id_etapa,
              objetivo=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg",
              reto=reto).save()

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
            'recompensa_texto': 'Recompensa RETO VIEWS',
            'categoria': 'economia',

            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '2',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-id_etapa': id_etapa,
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': 'Objetivo ETAPA VIEWS',

            # Nueva Etapa
            'form-0-id_etapa': '',
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': 'Objetivo NUEVO Etapa VIEWS',
        }

        resp = self.client.post(f'/editar_reto/{id_reto}', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)


##########################################################################################
# Comprobamos el funcionamiento de calificar y añadir prueba y ánimo en reto
class CalificarPruebaAnimoEtapaTest(TestCase):
    def setUpTestData(cls):
        # Creamos usuarios
        usuario = Usuario.objects.create_user(email="calificaretapa_view@yopuedo.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil
                                              =f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")
        # Creamos futuro animador
        usuario_animador = Usuario.objects.create_user(
            email="animadoretapa_view@yopuedo.com",
            nombre="María Jesús", password="Password1.",
            clave_aleatoria="clavealeat",
            clave_fija="clavefijausuario",
            foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        Usuario.objects.create_user(email="extraño_view@yopuedo.com",
                                    nombre="María Jesús", password="Password1.",
                                    clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        # Creamos el reto
        reto = Reto(id_reto="RETCALIFICARETAPA012345678901234567890123456789012",
                    titulo="PRUEBA RETO VIEWS",
                    objetivo="OBJETIVO RETO VIEWS",
                    categoria="inteligencia",
                    recompensa=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg",
                    coordinador=usuario, estado="En proceso")
        reto.save()

        # Creamos la primera etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(0),
              objetivo=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg",
              reto=reto, estado="En proceso").save()

        # Creamos la segunda etapa del reto
        Etapa(id_etapa=Utils.crear_id_etapa(1), objetivo=f"OBJETIVO ETAPA VIEWS",
              reto=reto).save()

        # Añadimos como participante el coordinador
        participante = Participante()
        participante.save()
        participante.usuario.add(usuario)
        participante.reto.add(reto)
        participante.save()

        # Añadimos animador y superanimador
        animador = Animador()
        animador.save()
        animador.usuario.add(usuario_animador)
        animador.reto.add(reto)
        animador.superanimador = False
        animador.save()

    def calificarVacio(self):
        self.client.login(username="calificaretapa_view@yopuedo.com",
                          password='Password1.')
        data = {
            'calificacion': ''
        }

        reto = Reto.objects.get(
            id_reto="RETCALIFICARETAPA012345678901234567890123456789012")
        etapas = reto.etapa_set.all()
        etapa = etapas.first()
        ultima_etapa = etapas.last()

        resp = self.client.get(f'/calificar/{etapa.id_etapa}', data)
        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(len(etapa.calificacion_set.all()), 0)
        self.assertEqual(etapa.estado, "En proceso")
        self.assertEqual(ultima_etapa.estado, "Propuesto")
        self.assertEqual(reto.estado, "En proceso")

    def calificarExtraño(self):
        self.client.login(username="extraño_view@yopuedo.com",
                          password='Password1.')
        data = {
            'calificacion': 'normal'
        }

        reto = Reto.objects.get(
            id_reto="RETCALIFICARETAPA012345678901234567890123456789012")
        etapas = reto.etapa_set.all()
        etapa = etapas.first()
        ultima_etapa = etapas.last()

        resp = self.client.get(f'/calificar/{etapa.id_etapa}', data)
        self.assertEqual(resp.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(len(etapa.calificacion_set.all()), 0)
        self.assertEqual(etapa.estado, "En proceso")
        self.assertEqual(ultima_etapa.estado, "Propuesto")
        self.assertEqual(reto.estado, "En proceso")

    def añadirPrueba(self):
        self.client.login(username="calificaretapa_view@yopuedo.com",
                          password='Password1.')
        data = {
            'prueba_texto': 'Esto es una prueba'
        }

        reto = Reto.objects.get(
            id_reto="RETCALIFICARETAPA012345678901234567890123456789012")
        etapa = reto.etapa_set.first()

        resp = self.client.post(f'/prueba/{etapa.id_etapa}', data)
        self.assertEqual(resp.status_code, HTTPStatus.CREATED)
        self.assertEqual(len(etapa.prueba_set.all()), 1)

    def getPrueba(self):
        self.client.login(username="calificaretapa_view@yopuedo.com",
                          password='Password1.')

        reto = Reto.objects.get(
            id_reto="RETCALIFICARETAPA012345678901234567890123456789012")
        etapa = reto.etapa_set.first()

        resp = self.client.get(f'/prueba/{etapa.id_etapa}')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)

    def añadirAnimo(self):
        self.client.login(username="animadoretapa_view@yopuedo.com",
                          password='Password1.')
        data = {
            'animo_texto': 'Esto es un ánimo del animador'
        }

        reto = Reto.objects.get(
            id_reto="RETCALIFICARETAPA012345678901234567890123456789012")
        etapa = reto.etapa_set.first()

        resp = self.client.post(f'/animo/{etapa.id_etapa}', data)
        self.assertEqual(resp.status_code, HTTPStatus.CREATED)
        self.assertEqual(len(etapa.animo_set.all()), 1)

        participantes = reto.participante_set.all()
        for participante in participantes:
            self.assertTrue(Notificacion.objects.filter(usuario=participante).exists())

    def getAnimoParticipante(self):
        self.client.login(username="calificaretapa_view@yopuedo.com",
                          password='Password1.')

        reto = Reto.objects.get(
            id_reto="RETCALIFICARETAPA012345678901234567890123456789012")
        etapa = reto.etapa_set.first()

        resp = self.client.get(f'/animo/{etapa.id_etapa}')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)

    def getAnimoAnimador(self):
        self.client.login(username="animadoretapa_view@yopuedo.com",
                          password='Password1.')

        reto = Reto.objects.get(
            id_reto="RETCALIFICARETAPA012345678901234567890123456789012")
        etapa = reto.etapa_set.first()

        resp = self.client.get(f'/animo/{etapa.id_etapa}')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)

    def calificarPrimera(self):
        self.client.login(username="calificaretapa_view@yopuedo.com",
                          password='Password1.')
        data = {
            'calificacion': 'normal'
        }

        reto = Reto.objects.get(
            id_reto="RETCALIFICARETAPA012345678901234567890123456789012")
        etapas = reto.etapa_set.all()
        etapa = etapas.first()
        ultima_etapa = etapas.last()

        resp = self.client.get(f'/calificar/{etapa.id_etapa}', data)
        self.assertEqual(resp.status_code, HTTPStatus.CREATED)
        self.assertEqual(len(etapa.calificacion_set.all()), 1)
        self.assertEqual(etapa.estado, "Finalizado")
        self.assertEqual(ultima_etapa.estado, "En proceso")
        self.assertEqual(reto.estado, "En proceso")

    def calificarUltima(self):
        self.client.login(username="calificaretapa_view@yopuedo.com",
                          password='Password1.')
        data = {
            'calificacion': 'normal'
        }

        reto = Reto.objects.get(
            id_reto="RETCALIFICARETAPA012345678901234567890123456789012")
        etapas = reto.etapa_set.all()
        etapa = etapas.first()
        ultima_etapa = etapas.last()

        resp = self.client.get(f'/calificar/{ultima_etapa.id_etapa}', data)
        self.assertEqual(resp.status_code, HTTPStatus.CREATED)
        self.assertEqual(len(ultima_etapa.calificacion_set.all()), 1)
        self.assertEqual(etapa.estado, "Finalizado")
        self.assertEqual(ultima_etapa.estado, "Finalizado")
        self.assertEqual(reto.estado, "Finalizado")


##########################################################################################

# Comprobamos el funcionamiento de la URL perfil
class PerfilViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        data = {
            'email': "perfil_view@yopuedo.com",
            'nombre': "María Jesús",
            'password': 'Password1.',
            'password_again': 'Password1.',
            'foto_de_perfil': SimpleUploadedFile(foto_perfil.name, foto_perfil.read())
        }
        client = Client()
        client.post('/registrarse/', data, format='multipart')

    def test_url_no_accesible(self):
        resp = self.client.get('/mi_perfil/')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue('/registrarse/' in resp.url)

    def test_url_accesible(self):
        self.client.login(username='perfil_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/mi_perfil/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_cerrar_sesion(self):
        self.client.login(username='perfil_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/cerrar_sesion/')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_get_modificar(self):
        self.client.login(username='perfil_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/editar_perfil/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_get_modificar_no_login(self):
        resp = self.client.get('/editar_perfil/')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue('/registrarse/' in resp.url)

    def test_post_modificar(self):
        self.client.login(username='perfil_view@yopuedo.com', password="Password1.")

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        data = {
            'email': "perfil_view@yopuedo.com",
            'nombre': "María Jesús López",
            'password_antigua': 'Password1.',
            'password_nueva': 'Password1.!',
            'password_again': 'Password1.!',
            'foto_de_perfil': SimpleUploadedFile(foto_perfil.name, foto_perfil.read())
        }
        resp = self.client.post('/editar_perfil/', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.ACCEPTED)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
        user = Usuario.objects.get(email="perfil_view@yopuedo.com")
        self.assertEqual(user.nombre, "María Jesús López")
        self.assertFalse(user.check_password("Password1."))
        self.assertTrue(user.check_password("Password1.!"))

    def test_eliminar(self):
        usuario = Usuario.objects.get(email='perfil_view@yopuedo.com')
        clave_aleatoria = usuario.clave_aleatoria
        self.client.login(username='perfil_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/eliminar/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        usuario = Usuario.objects.filter(email='perfil_view@yopuedo.com')
        self.assertTrue(usuario.exists())
        usuario = Usuario.objects.get(email='perfil_view@yopuedo.com')
        self.assertNotEqual(usuario.clave_aleatoria, clave_aleatoria)


##########################################################################################

# Comprobamos el funcionamiento de la URL perfil
class AmigosViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        usuario1 = Usuario.objects.create_user(email="amigos_view@yopuedo.com",
                                               nombre="María Jesús",
                                               password="Password1.",
                                               clave_aleatoria="clavealeat",
                                               clave_fija="clavefijausuario",
                                               foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        usuario2 = Usuario.objects.create_user(email="amigo1_view@yopuedo.com",
                                               nombre="María Jesús",
                                               password="Password1.",
                                               clave_aleatoria="clavealeat",
                                               clave_fija="clavefijausuario",
                                               foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        Usuario.objects.create_user(email="extrano_amigo_view@yopuedo.com",
                                    nombre="María Jesús",
                                    password="Password1.",
                                    clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        amistad = Amistad()
        amistad.save()
        amistad.amigo.add(usuario1)
        amistad.otro_amigo.add(usuario2)
        amistad.save()

    def test_amigos_url_no_accesible(self):
        resp = self.client.get('/mis_amigos/')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue('/registrarse/' in resp.url)

    def test_amigos_url_accesible(self):
        self.client.login(username='amigos_view@yopuedo.com', password="Password1.")

        resp = self.client.get('/mis_amigos/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_ver_perfil_amigo(self):
        self.client.login(username='amigos_view@yopuedo.com', password='Password1.')

        resp = self.client.get('/perfil/amigo1_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_ver_perfil_extraño(self):
        self.client.login(username='amigos_view@yopuedo.com', password='Password1.')

        resp = self.client.get('/perfil/extrano_amigo_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    def test_ver_perfil_no_accesible(self):
        resp = self.client.get('/perfil/amigo1_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue('/registrarse/' in resp.url)

    def test_nuevos_amigos_accesible(self):
        self.client.login(username='amigos_view@yopuedo.com', password='Password1.')

        resp = self.client.get('/nuevos_amigos/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_nuevos_amigos_no_accesible(self):
        resp = self.client.get('/nuevos_amigos/')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue('/registrarse/' in resp.url)

    def test_nuevos_amigos(self):
        self.client.login(username='amigos_view@yopuedo.com', password='Password1.')

        data = {
            "amigos": [json.dumps({"email": "extrano_amigo_view@yopuedo.com",
                                   "nombre": "María Jesús",
                                   "foto_perfil": "/media/YoPuedo/foto_perfil/mariajesus@gmail.com"
                                                  ".jpg"})]
        }

        resp = self.client.post('/nuevos_amigos/', data)
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue('/mis_amigos/' in resp.url)

        notificacion = Notificacion.objects.filter(
            usuario__email="extrano_amigo_view@yopuedo.com",
            enlace='/solicitud_amistad/amigos_view@yopuedo.com')

        self.assertTrue(notificacion.exists())

    def test_solicitud_amistad_no_existente(self):
        self.client.login(username='amigos_view@yopuedo.com', password='Password1.')

        resp = self.client.get('/solicitud_amistad/amigo1_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue('/perfil/' in resp.url)

    def test_solicitud_amistad_existente(self):
        self.client.login(username='extrano_amigo_view@yopuedo.com',
                          password='Password1.')

        resp = self.client.get('/solicitud_amistad/amigos_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_solicitud_amistad_no_accesible(self):
        resp = self.client.get('/solicitud_amistad/amigo1_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue('/registrarse/' in resp.url)

    def test_rechazar_no_accesible(self):
        resp = self.client.get('/rechazar/amigo1_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue('/registrarse/' in resp.url)

    def test_rechazar(self):
        self.client.login(username='amigos_view@yopuedo.com', password='Password1.')

        data = {
            "amigos": [json.dumps({"email": "extrano_amigo_view@yopuedo.com",
                                   "nombre": "María Jesús",
                                   "foto_perfil": "/media/YoPuedo/foto_perfil/mariajesus@gmail.com"
                                                  ".jpg"})]
        }

        self.client.post('/nuevos_amigos/', data)
        self.client.logout()

        self.client.login(username='extrano_amigo_view@yopuedo.com',
                          password='Password1.')

        resp = self.client.get('/rechazar/amigos_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue('/mis_amigos/' in resp.url)

        notificacion = Notificacion.objects.filter(
            usuario__email="extrano_amigo_view@yopuedo.com",
            enlace='/solicitud_amistad/amigos_view@yopuedo.com')

        self.assertFalse(notificacion.exists())

    def test_aceptar(self):
        self.client.login(username='amigos_view@yopuedo.com', password='Password1.')

        data = {
            "amigos": [json.dumps({"email": "extrano_amigo_view@yopuedo.com",
                        "nombre": "María Jesús",
                       "foto_perfil": "/media/YoPuedo/foto_perfil/mariajesus@gmail.com"
                                      ".jpg"})]
        }

        self.client.post('/nuevos_amigos/', data)
        self.client.logout()

        self.client.login(username='extrano_amigo_view@yopuedo.com',
                          password='Password1.')

        resp = self.client.get(
            '/validar_clave/amigos_view@yopuedo.com/extrano_amigo_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

        clave_aleatoria = Usuario.objects.get(
            email='extrano_amigo_view@yopuedo.com').clave_aleatoria

        data = {
            'email': 'extrano_amigo_view@yopuedo.com',
            'contador': 0,
            'clave': clave_aleatoria
        }

        resp = self.client.post(
            '/validar_clave/amigos_view@yopuedo.com/extrano_amigo_view@yopuedo.com',
            data)
        self.assertEqual(resp.status_code, HTTPStatus.ACCEPTED)

        notificacion = Notificacion.objects.filter(
            usuario__email="extrano_amigo_view@yopuedo.com",
            enlace='/solicitud_amistad/amigos_view@yopuedo.com')

        self.assertFalse(notificacion.exists())

        amistad = Amistad.objects.filter(
            amigo__email='extrano_amigo_view@yopuedo.com',
            otro_amigo__email='amigos_view@yopuedo.com'
        )

        self.assertTrue(amistad.exists())

    def test_aceptar_no_usuario(self):
        self.client.login(username='extrano_amigo_view@yopuedo.com',
                          password='Password1.')

        data = {
            'email': 'extrano_amigo_view@yopuedo.com',
            'contador': 0,
            'clave': "clavefijausuario"
        }

        resp = self.client.post(
            '/validar_clave/no_usuario_view@yopuedo.com/extrano_amigo_view@yopuedo.com',
            data)
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    def test_dejar_seguir_no_accesible(self):
        resp = self.client.post('/eliminar_amigo/amigo1_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue('/registrarse/' in resp.url)

    def test_dejar_seguir_extraño(self):
        self.client.login(username='extrano_amigo_view@yopuedo.com',
                          password='Password1.')

        resp = self.client.post('/eliminar_amigo/amigo_noconocido_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    def test_dejar_seguir(self):
        self.client.login(username='amigo1_view@yopuedo.com',
                          password='Password1.')

        resp = self.client.post('/eliminar_amigo/amigos_view@yopuedo.com')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue(resp.url, '/mis_amigos/')

        amistad = Amistad.objects.filter(
            amigo__email='extrano_amigo_view@yopuedo.com',
            otro_amigo__email='amigos_view@yopuedo.com'
        )

        self.assertFalse(amistad.exists())


##########################################################################################

# Comprobamos el funcionamiento de la URL de Notificaciones

class NotificacionesTestView(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create_user(email="notificacion_view@yopuedo.com",
                                    nombre="María Jesús",
                                    password="Password1.",
                                    clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

    def test_contador_sin_notificacion(self):
        self.client.login(username='notificacion_view@yopuedo.com',
                          password='Password1.')

        content = '''<i class="bi bi-bell-fill"></i>Notificaciones'''

        resp = self.client.get('/contador_notificaciones/')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertEqual(resp.content, content)

    def test_contador_con_notificacion(self):

        usuario = Usuario.objects.get(email="notificacion_view@yopuedo.com")

        notificacion = Notificacion()
        notificacion.usuario = usuario
        notificacion.categoria = 'Amistad'
        notificacion.enlace = f'/solicitud_amistad/usuario@usuario.es'
        notificacion.mensaje = f"Usuario1 te ha mandado una solicitud " \
                               f"de amistad para que seas su amigo. " \
                               f"¿Quieres aceptarla?"
        notificacion.save()

        self.client.login(username='notificacion_view@yopuedo.com',
                          password='Password1.')

        content = '''<i class="bi bi-bell-fill"></i>Notificaciones
        <span class="top-0 start-100 translate-middle badge rounded-pill 
        bg-danger">0</span>'''

        resp = self.client.get('/contador_notificaciones/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(resp.content, content)
