from django.test import TestCase
from ..models import Usuario, Reto, Etapa, Animador, Participante
from ..utils import Utils


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


# Comprobamos el funcionamiento de la tabla RETO, ETAPA, ANIMADOR, PARTICIPANTE
class RetoModelTest(TestCase):
    def setUpTestData(self):
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
        reto = Reto.objects.create(
            id_reto="RET123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL",
            titulo="Prueba RETO",
            objetivo="Objetivo RETO",
            recompensa="Recompensa RETO",
            categoria="economia",
            coordinador=usuario
        )

        Etapa.objects.create(
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

        participante = Participante()
        participante.save()
        participante.reto.add(reto)
        participante.usuario.add(usuario)

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
        animadores = Animador.objects.filter(reto=reto)
        usuario = Usuario.objects.get(email="maria@jesus.com")

        for animador in animadores:
            self.assertEqual(animador.reto, reto)
            self.assertEqual(animador.usuario, usuario)
            self.assertFalse(animador.superanimador)

    def test_participantes(self):
        reto = Reto.objects.get(
            id_reto="RET123456789abcdefghijklmnñopqrstuwxyzABCDEFGHIJKL")
        participantes = Participante.objects.filter(reto=reto)
        usuario = Usuario.objects.get(email="maria@jesus.com")

        for participante in participantes:
            self.assertEqual(participante.reto, reto)
            self.assertEqual(participante.usuario, usuario)
