from django.db.models import Q
from django.test import TestCase
from ..models import *


##########################################################################################

# Comprobamos el funcionamiento de la tabla USUARIO
class UsuarioModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create_user(email="mariajesus@gmail.com", nombre="María Jesús",
                                    password="Password1.", clave_fija='clave_fija',
                                    clave_aleatoria='clave_aleatoria',
                                    foto_perfil="/media/YoPuedo/foto_perfil/mariajesus@gmail.com")

    def test_email(self):
        usuario = Usuario.objects.get(email="mariajesus@gmail.com")
        self.assertEqual(usuario.email, 'mariajesus@gmail.com')

    def test_nombre(self):
        usuario = Usuario.objects.get(email="mariajesus@gmail.com")
        self.assertEqual(usuario.nombre, 'María Jesús')

    def test_password(self):
        usuario = Usuario.objects.get(email="mariajesus@gmail.com")
        self.assertTrue(usuario.check_password('Password1.'))

    def test_foto_perfil(self):
        usuario = Usuario.objects.get(email="mariajesus@gmail.com")
        self.assertEqual(usuario.foto_perfil,
                         "/media/YoPuedo/foto_perfil/mariajesus@gmail.com")


##########################################################################################

# Comprobamos el funcionamiento de las tablas RETO, ETAPA, ANIMADOR, PARTICIPANTE,
# CALIFICACION
class RetoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        usuario = Usuario.objects.create_user(email="reto@gmail.com",
                                              nombre="María Jesús",
                                              password="Password1.",
                                              clave_fija='clave_fija',
                                              clave_aleatoria='clave_aleatoria',
                                              foto_perfil="/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        usuario1 = Usuario.objects.create_user(email="maria@jesus.com",
                                               nombre="María López",
                                               password="Password",
                                               clave_fija='clave_fija',
                                               clave_aleatoria='clave_aleatoria',
                                               foto_perfil="/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        usuario2 = Usuario.objects.create_user(email="mariajesus@jesus.com",
                                               nombre="María López",
                                               password="Password",
                                               clave_fija='clave_fija',
                                               clave_aleatoria='clave_aleatoria',
                                               foto_perfil="/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        reto = Reto.objects.create(
            id_reto="RET123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL",
            titulo="Prueba RETO",
            objetivo="Objetivo RETO",
            recompensa="Recompensa RETO",
            categoria="economia",
            coordinador=usuario
        )

        etapa = Etapa.objects.create(
            id_etapa="ETP123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL",
            reto=reto,
            objetivo="Objetivo ETAPA"
        )

        animador = Animador()
        animador.save()
        animador.reto.add(reto)
        animador.usuario.add(usuario1)
        animador.superanimador = False
        animador.save()

        animador2 = Animador()
        animador2.save()
        animador2.reto.add(reto)
        animador2.usuario.add(usuario2)
        animador2.superanimador = True
        animador2.save()

        participante = Participante()
        participante.save()
        participante.reto.add(reto)
        participante.usuario.add(usuario)

        calificacion = Calificacion()
        calificacion.save()
        calificacion.etapa.add(etapa)
        calificacion.participante.add(participante)
        calificacion.calificacion = 'muy buena'
        calificacion.save()

        prueba = Prueba()
        prueba.save()
        prueba.etapa.add(etapa)
        prueba.participante.add(participante)
        prueba.prueba = "Prueba etapa reto"
        prueba.save()

        animo = Animo()
        animo.save()
        animo.etapa.add(etapa)
        animo.animador.add(animador)
        animo.mensaje = "Ánimo etapa reto"
        animo.save()

        animo = Animo()
        animo.save()
        animo.etapa.add(etapa)
        animo.animador.add(animador2)
        animo.mensaje = "Superánimo etapa reto"
        animo.save()

    def test_reto(self):
        reto = Reto.objects.get(
            id_reto="RET123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL")
        usuario = Usuario.objects.get(email="reto@gmail.com")

        self.assertEqual(reto.titulo, "Prueba RETO")
        self.assertEqual(reto.objetivo, "Objetivo RETO")
        self.assertEqual(reto.categoria, "economia")
        self.assertEqual(reto.recompensa, "Recompensa RETO")
        self.assertEqual(reto.coordinador, usuario)

    def test_etapa(self):
        etapa = Etapa.objects.get(
            id_etapa="ETP123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL")
        reto = Reto.objects.get(
            id_reto="RET123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL")

        self.assertEqual(etapa.reto, reto)
        self.assertEqual(etapa.objetivo, "Objetivo ETAPA")
        self.assertEqual(etapa.estado, "Propuesto")

    def test_animadores(self):
        reto = Reto.objects.get(
            id_reto="RET123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL")
        animador = reto.animador_set.first()

        self.assertFalse(animador.superanimador)

    def test_participantes(self):
        reto = Reto.objects.get(
            id_reto="RET123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL")
        participante = reto.participante_set.first()

        self.assertEqual(participante.usuario.first().email, "reto@gmail.com")

    def test_calificacion(self):
        etapa = Etapa.objects.get(
            id_etapa="ETP123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL")
        participante = etapa.reto.participante_set.first()
        calificacion = etapa.calificacion_set.first()

        self.assertEqual(calificacion.etapa.first(), etapa)
        self.assertEqual(calificacion.participante.first(), participante)
        self.assertEqual(calificacion.calificacion, "muy buena")

    def test_prueba(self):
        etapa = Etapa.objects.get(
            id_etapa="ETP123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL")
        participante = etapa.reto.participante_set.first()
        prueba = etapa.prueba_set.first()

        self.assertEqual(prueba.etapa.first(), etapa)
        self.assertEqual(prueba.participante.first(), participante)
        self.assertEqual(prueba.prueba, "Prueba etapa reto")

    def test_animo_animador(self):
        etapa = Etapa.objects.get(
            id_etapa="ETP123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL")
        animador = etapa.reto.animador_set.first()
        animos = etapa.animo_set.filter(animador=animador).all()
        animo = animos.first()

        self.assertEqual(len(animos), 1)
        self.assertEqual(animo.etapa.first(), etapa)
        self.assertEqual(animo.animador.first(), animador)
        self.assertEqual(animo.mensaje, "Ánimo etapa reto")

    def test_animo_superanimador(self):
        etapa = Etapa.objects.get(
            id_etapa="ETP123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL")
        animador = etapa.reto.animador_set.first()
        superanimador = etapa.reto.animador_set.last()
        animos = etapa.animo_set.all()
        primer_animo = animos.first()
        ultimo_animo = animos.last()

        self.assertEqual(len(animos), 2)
        self.assertEqual(primer_animo.etapa.first(), etapa)
        self.assertEqual(primer_animo.animador.first(), animador)
        self.assertEqual(primer_animo.mensaje, "Ánimo etapa reto")
        self.assertEqual(ultimo_animo.etapa.first(), etapa)
        self.assertEqual(ultimo_animo.animador.first(), superanimador)
        self.assertEqual(ultimo_animo.mensaje, "Superánimo etapa reto")


##########################################################################################

# Comprobamos el funcionamiento de la tabla AMISTAD
class AmistadModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        usuario1 = Usuario.objects.create_user(email="amistad1@gmail.com",
                                               nombre="María Jesús",
                                               password="Password1.",
                                               clave_fija='clave_fija',
                                               clave_aleatoria='clave_aleatoria',
                                               foto_perfil="/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        usuario2 = Usuario.objects.create_user(email="amistad2@gmail.com",
                                               nombre="María Jesús",
                                               password="Password1.",
                                               clave_fija='clave_fija',
                                               clave_aleatoria='clave_aleatoria',
                                               foto_perfil="/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        amistad = Amistad()
        amistad.save()
        amistad.amigo.add(usuario1)
        amistad.otro_amigo.add(usuario2)
        amistad.save()

    def test_amistad(self):
        amistad = Amistad.objects.last()

        self.assertEqual(amistad.amigo.first().email, "amistad1@gmail.com")
        self.assertEqual(amistad.otro_amigo.first().email, "amistad2@gmail.com")


##########################################################################################

# Comprobamos el funcionamiento de la tabla NOTIFICACIÓN
class NotificacionModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        usuario = Usuario.objects.create_user(email="notificacion@gmail.com",
                                              nombre="María Jesús",
                                              password="Password1.",
                                              clave_fija='clave_fija',
                                              clave_aleatoria='clave_aleatoria',
                                              foto_perfil="/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

        notificacion = Notificacion()
        notificacion.mensaje = "Esto es la primera prueba"
        notificacion.usuario = usuario
        notificacion.enlace = "/enlace/"
        notificacion.categoria = "Prueba"
        notificacion.save()

    def test_notificacion(self):
        notificacion = Notificacion.objects.get(id_notificacion="1")

        self.assertEqual(notificacion.mensaje, "Esto es la primera prueba")
        self.assertEqual(notificacion.usuario.nombre, "María Jesús")
        self.assertEqual(notificacion.enlace, "/enlace/")
