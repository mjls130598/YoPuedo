from django.contrib.auth import login
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from TFM.settings import BASE_DIR
from http import HTTPStatus
from django.test.client import Client

from ..models import Usuario, Reto, Etapa, Animador, Participante, Amistad
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
        Usuario.objects.create_user(email="misretos_view@gmail.com",
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

# Comprobamos el funcionamiento de la URL obtener retos de un estado
class GetRetosTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Creamos usuarios
        usuario = Usuario.objects.create_user(email="getretos_view@gmail.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        otro_usuario = Usuario.objects.create_user(email="getretos_otro_view@gmail.com",
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
        Etapa(id_etapa=Utils.crear_id_etapa(), objetivo="ETAPA 1 RETO VIEWS",
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
        Etapa(id_etapa=Utils.crear_id_etapa(), objetivo="ETAPA 1 RETO 2 VIEWS",
              reto=reto2).save()

        # Creamos participantes en el reto
        participante = Participante()
        participante.save()
        participante.reto = reto2
        participante.usuario = otro_usuario

    def get_propuesto_individual(self):
        # Logueamos el primer usuario
        self.client.login(username='getretos_view@gmail.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=individuales&estado=propuesto')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 1)

    def get_propuesto_colectivo(self):
        # Logueamos el primer usuario
        self.client.login(username='getretos_view@gmail.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=colectivos&estado=propuesto')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 0)

    def get_animando_individual(self):
        # Logueamos el segundo usuario
        self.client.login(username='getretos_otro_view@gmail.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=individuales&estado=animando')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 1)

    def get_animando_colectivo(self):
        # Logueamos el segundo usuario
        self.client.login(username='getretos_otro_view@gmail.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=colectivos&estado=animando')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 0)

    def get_finalizado_individual(self):
        # Logueamos el segundo usuario
        self.client.login(username='getretos_otro_view@gmail.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=individuales&estado=finalizados')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 0)

    def get_finalizado_colectivos(self):
        # Logueamos el segundo usuario
        self.client.login(username='getretos_otro_view@gmail.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=colectivos&estado=finalizados')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 1)

    def get_proceso_individual(self):
        # Logueamos el primer usuario
        self.client.login(username='getretos_view@gmail.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=individuales&estado=proceso')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 0)

    def get_proceso_colectivos(self):
        # Logueamos el primer usuario
        self.client.login(username='getretos_view@gmail.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=colectivos&estado=proceso')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 0)

    def get_categoria_individual(self):
        # Logueamos el primer usuario
        self.client.login(username='getretos_view@gmail.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=individuales&categoria=inteligencia&estado'
                               '=propuesto')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 1)

    def get_no_categoria_colectivo(self):
        # Logueamos el primer usuario
        self.client.login(username='getretos_view@gmail.com', password="Password1.")

        resp = self.client.get('/retos/?tipo=colectivos&categoria=inteligencia&estado'
                               '=propuesto')
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertEqual(len(resp.context['retos']), 0)


##########################################################################################

# Comprobamos el funcionamiento de la URL nuevo reto
class NuevoRetoTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        usuario = Usuario.objects.create_user(email="nuevoreto_view@gmail.com",
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
        cls.client = Client()
        cls.user = usuario

    def test_url_accesible(self):
        self.client.login(username='nuevoreto_view@gmail.com', password="Password1.")

        resp = self.client.get('/nuevo_reto/')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_url_tipo_accesible(self):
        self.client.login(username='nuevoreto_view@gmail.com', password="Password1.")

        resp = self.client.get('/nuevo_reto/?tipo=individual')
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    def test_post_reto_individual(self):
        self.client.login(username='nuevoreto_view@gmail.com', password="Password1.")

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
        self.assertTrue("/mis_retos/" in resp.url)
        id_reto = resp.url[-50:]
        self.assertTrue(Reto.objects.filter(id_reto=id_reto).exists())
        self.assertTrue(Etapa.objects.filter(reto__id_reto=id_reto).exists())
        self.assertEqual(Participante.objects.filter(reto__id_reto=id_reto).
                         last().usuario.all().first().email, "nuevoreto_view@gmail.com")

    def test_post_reto_individual_animadores(self):
        self.client.login(username='nuevoreto_view@gmail.com', password="Password1.")

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
            'animador': ["animador_view@gmail.com"],
            'superanimador-animador_view@gmail.com': 'false'
        }

        resp = self.client.post('/nuevo_reto/?tipo=individual', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue("/mis_retos/" in resp.url)
        id_reto = resp.url[-50:]
        self.assertTrue(Reto.objects.filter(id_reto=id_reto).exists())
        self.assertTrue(Etapa.objects.filter(reto__id_reto=id_reto).exists())
        self.assertEqual(Participante.objects.filter(reto__id_reto=id_reto).
                         last().usuario.all().first().email, "nuevoreto_view@gmail.com")
        self.assertTrue(Animador.objects.filter(reto__id_reto=id_reto).exists())

    def test_post_reto_colectivo(self):
        self.client.login(username='nuevoreto_view@gmail.com', password="Password1.")

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
            'animador': ["animador_view@gmail.com"],
            'superanimador-animador_view@gmail.com': 'false',

            # Participantes
            'participante': ["participante_view@gmail.com"]
        }

        resp = self.client.post('/nuevo_reto/?tipo=colectivo', data, format='multipart')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertTrue("/mis_retos/" in resp.url)
        id_reto = resp.url[-50:]
        self.assertTrue(Reto.objects.filter(id_reto=id_reto).exists())
        self.assertTrue(Etapa.objects.filter(reto__id_reto=id_reto).exists())
        self.assertEqual(Participante.objects.filter(reto__id_reto=id_reto).
                         last().usuario.all().first().email, "nuevoreto_view@gmail.com")
        self.assertTrue(Animador.objects.filter(reto__id_reto=id_reto).exists())
        self.assertEqual(len(Participante.objects.filter(reto__id_reto=id_reto).all()), 2)


##########################################################################################

# Comprobamos el funcionamiento de la URL obtener amistades
class GetAmigosTest(TestCase):
    def setUpTestData(cls):
        usuario = Usuario.objects.create_user(email="amigo_view@gmail.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        usuario2 = Usuario.objects.create_user(email="amigo2_view@gmail.com",
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
        self.client.login(username='amigo_view@gmail.com', password='Password1.')
        resp = self.client.get('/amigos/')
        self.assertEqual(len(resp.context['amigos']), 1)
        self.assertEqual(resp.status_code, HTTPStatus.OK)


##########################################################################################

# Comprobamos el funcionamiento de la URL obtener reto
class GetRetoTest(TestCase):
    def setUpTestData(cls):
        # Creamos usuarios
        usuario = Usuario.objects.create_user(email="getreto_view@gmail.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        Usuario.objects.create_user(email="otro_view@gmail.com",
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
        Etapa(id_etapa=Utils.crear_id_etapa(), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

    def permitida_obtencion(self):
        self.client.login(username="getreto_view@gmail.com", password='Password1.')
        reto = Reto.objects.filter(coordinador__email='getreto_view@gmail.com').first()
        resp = self.client.get(f'/reto/{reto.id_reto}')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)

    def no_permitida_obtencion(self):
        self.client.login(username="otro_view@gmail.com", password='Password1.')
        reto = Reto.objects.filter(coordinador__email='getreto_view@gmail.com').first()
        resp = self.client.get(f'/reto/{reto.id_reto}')
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)


##########################################################################################

# Comprobamos el funcionamiento de la URL iniciar reto
class IniciarRetoTest(TestCase):
    def setUpTestData(cls):
        # Creamos usuarios
        usuario = Usuario.objects.create_user(email="iniciarreto_view@gmail.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        otro_usuario = Usuario.objects.create_user(
            email="iniciarreto_otro_view@gmail.com",
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
        Etapa(id_etapa=Utils.crear_id_etapa(), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

        # Creamos el animador del reto
        animador = Animador()
        animador.save()
        animador.reto = reto
        animador.usuario = otro_usuario
        animador.superanimador = True
        animador.save()

    def permitida_obtencion(self):
        self.client.login(username="iniciarreto_view@gmail.com", password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='iniciarreto_view@gmail.com').first()
        resp = self.client.get(f'/iniciar_reto/{reto.id_reto}')
        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        reto = Reto.objects.filter(
            coordinador__email='iniciarreto_view@gmail.com').first()

        self.assertEqual(reto.estado, "En proceso")
        self.assertEqual(reto.etapa_set.first().estado, "En proceso")

    def no_permitida_obtencion(self):
        self.client.login(username="iniciarreto_otro_view@gmail.com",
                          password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='iniciarreto_view@gmail.com').first()
        resp = self.client.get(f'/iniciar_reto/{reto.id_reto}')
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)


##########################################################################################

# Comprobamos el funcionamiento de la URL eliminar reto
class EliminarRetoTest(TestCase):
    def setUpTestData(cls):
        # Creamos usuarios
        usuario = Usuario.objects.create_user(email="eliminarreto_view@gmail.com",
                                              nombre="María Jesús", password="Password1.",
                                              clave_aleatoria="clavealeat",
                                              clave_fija="clavefijausuario",
                                              foto_perfil=f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        otro_usuario = Usuario.objects.create_user(
            email="eliminarreto_otro_view@gmail.com",
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
        Etapa(id_etapa=Utils.crear_id_etapa(), objetivo="ETAPA 1 RETO VIEWS",
              reto=reto).save()

        # Creamos el animador del reto
        animador = Animador()
        animador.save()
        animador.reto = reto
        animador.usuario = otro_usuario
        animador.superanimador = True
        animador.save()

    def permitida_obtencion(self):
        self.client.login(username="eliminarreto_view@gmail.com", password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='eliminarreto_view@gmail.com').first()
        resp = self.client.get(f'/eliminar_reto/{reto.id_reto}')

        self.assertEqual(resp.status_code, HTTPStatus.FOUND)
        self.assertFalse(Reto.objects.filter(id_reto=reto.id_reto).exists())
        self.assertFalse(Etapa.objects.filter(reto__id_reto=reto.id_reto).exists())
        self.assertFalse(Animador.objects.filter(reto__id_reto=reto.id_reto).exists())

    def no_permitida_obtencion(self):
        self.client.login(username="eliminarreto_otro_view@gmail.com",
                          password='Password1.')
        reto = Reto.objects.filter(
            coordinador__email='eliminarreto_view@gmail.com').first()
        resp = self.client.get(f'/eliminar_reto/{reto.id_reto}')
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)
