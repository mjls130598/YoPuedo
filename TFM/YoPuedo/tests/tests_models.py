from django.test import TestCase
from ..models import Usuario, Reto, Etapa, Animador
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
    def setUpTestData(cls):
        usuario = Usuario.objects.create_user(email="mariajesus@gmail.com",
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
            id_reto=Utils.crear_id_reto(),
            titulo="Prueba RETO",
            objetivo="Objetivo RETO",
            recompensa="Recompensa RETO",
            categoria="economia",
            coordinador=usuario
        )

        Etapa.objects.create(
            id_etapa=Utils.crear_id_etapa(),
            reto=reto,
            objetivo="Objetivo ETAPA"
        )

        animador = Animador()
        animador.save()
        animador.reto.add(reto)
        animador.usuario.add(usuario1)
        animador.superanimador = False
        animador.save()

        animador = Animador()
        animador.save()
        animador.reto.add(reto)
        animador.usuario.add(usuario1)
