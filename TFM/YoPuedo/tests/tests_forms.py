from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import formset_factory
from django.test import TestCase
from ..forms import *
from TFM.settings import BASE_DIR
from ..models import Usuario


##########################################################################################

# Comprobamos la validación del formulario de registro
class RegistroFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create_user(email="mj@gmail.com", nombre="María Jesús",
                                    password="Password1.",
                                    clave_aleatoria="clave_aleatoria",
                                    clave_fija="clave_fija",
                                    foto_perfil="/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

    def test_correcto(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password1*',
            'password_again': 'Password1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertTrue(len(form.errors) == 0)

    def test_email_incorrecto(self):
        form_data = {
            'email': 'mariajesus@gmail',
            'nombre': 'María Jesús',
            'password': 'Password1*',
            'password_again': 'Password1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['email'], ['Introduzca una dirección de correo '
                                                'electrónico válida.'])

    def test_email_existente(self):
        form_data = {
            'email': 'mj@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password1*',
            'password_again': 'Password1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['email'], ['Ya existe una cuenta con ese email. '
                                                'Pruebe con otro.'])

    def test_nombre_largo(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús López Salmerón María Jesús López Salmerón María '
                      'Jesús López Salmerón María Jesús López Salmerón',
            'password': 'Password1*',
            'password_again': 'Password1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['nombre'], ["Asegúrese de que este valor tenga "
                                                 "menos de 100 caracteres (tiene 107)."])

    def test_no_coinciden_password(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password1*',
            'password_again': 'Password1',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['password_again'], ['Las contraseñas deben ser '
                                                         'iguales'])

    def test_password_no_numerico(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password*',
            'password_again': 'Password*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['password'], ['La contraseña debe contener al menos '
                                                   'un número'])

    def test_password_no_mayuscula(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'password1*',
            'password_again': 'password1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['password'], ['La contraseña debe tener al menos '
                                                   'una mayúscula'])

    def test_password_no_simbolos(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password1',
            'password_again': 'Password1',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['password'], ["La contraseña debe tener al menos "
                                                   "uno de estos símbolos: "
                                                   "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"])

    def test_password_no_minuscula(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'PASSWORD1*',
            'password_again': 'PASSWORD1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['password'],
                         ["La contraseña debe contener al menos una letra "
                          "en minúscula"])

    def test_foto_de_perfil_vacio(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password1*',
            'password_again': 'Password1*',
        }

        form = RegistroForm(data=form_data)

        self.assertEqual(form.errors['foto_de_perfil'], ['Este campo es obligatorio.'])

    def test_imagen_vacia(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password1*',
            'password_again': 'Password1',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/prueba.txt"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['foto_de_perfil'],
                         ['El fichero enviado está vacío.'])

    def test_no_imagen(self):
        form_data = {
            'email': 'mariajesus@gmail.com',
            'nombre': 'María Jesús',
            'password': 'Password1*',
            'password_again': 'Password1',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/prueba2.txt"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['foto_de_perfil'], ['Envíe una imagen válida. El '
                                                         'fichero que ha enviado no era '
                                                         'una imagen o se trataba de una '
                                                         'imagen corrupta.'])


##########################################################################################

# Comprobamos la validación del formulario de validar clave
class ClaveFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create_user(email="validar_clave@gmail.com", nombre="María Jesús",
                                    password="Password1.",
                                    clave_aleatoria="clavealeat",
                                    clave_fija="clavefijausuario",
                                    foto_perfil="/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

    def test_clave_aleatoria_valida(self):
        data = {
            'email': 'validar_clave@gmail.com',
            'contador': 0,
            'clave': 'clavealeat'
        }

        form = ClaveForm(data)
        self.assertTrue(len(form.errors) == 0)

    def test_clave_fija_valida(self):
        data = {
            'email': 'validar_clave@gmail.com',
            'contador': 0,
            'clave': 'clavefijausuario'
        }

        form = ClaveForm(data)
        self.assertTrue(len(form.errors) == 0)

    def test_clave_erronea(self):
        data = {
            'email': 'validar_clave@gmail.com',
            'contador': 0,
            'clave': 'clave_erronea'
        }

        form = ClaveForm(data)

        self.assertEqual(form.errors['clave'], ['La clave introducida es incorrecta. Por '
                                                'favor, introdúcela de nuevo.'])


##########################################################################################

# Comprobamos la validación del formulario de iniciar sesión
class InicioFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create_user(email="inicio@gmail.com", nombre="María Jesús",
                                    password="Password1.",
                                    clave_aleatoria="clave1",
                                    clave_fija="clave2",
                                    foto_perfil="/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

    def test_inicio_valido(self):
        data = {
            'email_sesion': 'inicio@gmail.com',
            'password_sesion': 'Password1.'
        }

        form = InicioForm(data)
        self.assertTrue(len(form.errors) == 0)

    def test_email_incorrecto(self):
        data = {
            'email_sesion': 'inicio_sesion@gmail.com',
            'password_sesion': 'Password1.'
        }

        form = InicioForm(data)
        self.assertEqual(form.errors['password_sesion'], ["Usuario y/o contraseña "
                                                          "incorrect@"])

    def test_password_incorrecto(self):
        data = {
            'email_sesion': 'inicio@gmail.com',
            'password_sesion': 'Password2.'
        }

        form = InicioForm(data)
        self.assertEqual(form.errors['password_sesion'], ["Usuario y/o contraseña "
                                                          "incorrect@"])


##########################################################################################

# Comprobamos la validación del formulario de nuevo reto - GENERAL
class RetoGeneralFormTest(TestCase):
    def test_campos_vacios(self):
        data = {}
        form = RetoGeneralForm(data)

        self.assertEqual(form.errors['titulo'], ['Debes indicar el título del reto',
                                                 'Debes escribir entre 10 y 500 caracteres'])
        self.assertEqual(form.errors['objetivo_texto'],
                         ['Debes indicar el objetivo del reto'])
        self.assertEqual(form.errors['recompensa_texto'],
                         ['Debes indicar la recompensa del reto'])
        self.assertEqual(form.errors['categoria'],
                         ['Debes indicar qué tipo de categoría es el reto'])

    def test_multiples_objetivo(self):
        data = {
            'titulo': 'Prueba Reto GENERAL',
            'objetivo_texto': 'Objetivo prueba'
        }

        objetivo_imagen = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        objetivo_imagen = open(objetivo_imagen, 'rb')

        form = RetoGeneralForm(data=data, files={'objetivo_imagen': SimpleUploadedFile(
            objetivo_imagen.name, objetivo_imagen.read())})

        self.assertEqual(form.errors['objetivo_texto'],
                         ['Elige una forma de indicar el objetivo del reto'])

    def test_multiples_multimedia_recompensa(self):
        data = {
            'titulo': 'Prueba Reto GENERAL'
        }

        recompensa_imagen = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        recompensa_imagen = open(recompensa_imagen, 'rb')

        recompensa_audio = f"{BASE_DIR}/media/YoPuedo/audio-ejemplo.mp3"
        recompensa_audio = open(recompensa_audio, 'rb')

        form = RetoGeneralForm(data=data, files={
            'recompensa_imagen': SimpleUploadedFile(recompensa_imagen.name,
                                                    recompensa_imagen.read()),
            'recompensa_audio': SimpleUploadedFile(recompensa_audio.name,
                                                   recompensa_audio.read())})

        self.assertEqual(form.errors['recompensa_texto'],
                         ['Elige una forma de indicar la recompensa del reto'])

    def test_general_correcto(self):
        data = {
            'titulo': 'Prueba RETO VIEWS',
            'objetivo_imagen': '',
            'objetivo_audio': '',
            'objetivo_video': '',
            'objetivo_texto': 'Objetivo RETO FORMS',
            'recompensa_imagen': '',
            'recompensa_audio': '',
            'recompensa_video': '',
            'recompensa_texto': 'Recompensa RETO FORMS',
            'categoria': 'economia',
        }

        form = RetoGeneralForm(data)
        self.assertEqual(len(form.errors), 0)


##########################################################################################

# Comprobamos la validación del formulario de nuevo reto - ETAPAS
class RetoEtapasTest(TestCase):

    def test_campos_vacios(self):
        data = {}
        form = RetoEtapaForm(data)

        self.assertEqual(form.errors['objetivo_texto'],
                         ['Debes indicar el objetivo de la etapa'])

    def test_multiples_objetivo(self):
        data = {
            'objetivo_texto': 'Objetivo prueba'
        }

        objetivo_imagen = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        objetivo_imagen = open(objetivo_imagen, 'rb')

        form = RetoEtapaForm(data=data, files={'objetivo_imagen': SimpleUploadedFile(
            objetivo_imagen.name, objetivo_imagen.read())})

        self.assertEqual(form.errors['objetivo_texto'],
                         ['Elige una forma de indicar el objetivo de la etapa'])

    def test_etapa_correcta(self):
        data = {
            'objetivo_texto': 'Objetivo prueba',
            'objetivo_imagen': '',
            'objetivo_audio': '',
            'objetivo_video': ''
        }

        form = RetoEtapaForm(data=data)

        self.assertEqual(len(form.errors), 0)

    def test_no_etapas(self):
        etapas_form_model = formset_factory(RetoEtapaForm, formset=EtapasFormSet,
                                            max_num=5)

        data = {
            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '1',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': '',
        }

        etapas_form = etapas_form_model(data)

        self.assertEqual(etapas_form.errors[0]['objetivo_texto'],
                         ['Debes indicar el objetivo de la etapa'])

    def test_etapa_vacia(self):
        etapas_form_model = formset_factory(RetoEtapaForm, formset=EtapasFormSet,
                                            max_num=5)

        data = {
            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '1',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': '',

            # 2º Etapa
            'form-1-objetivo_imagen': '',
            'form-1-objetivo_video': '',
            'form-1-objetivo_audio': '',
            'form-1-objetivo_texto': 'Objetivo 2º ETAPA',
        }

        etapas_form = etapas_form_model(data)

        self.assertEqual(etapas_form.errors[0]['objetivo_texto'],
                         ['Debes indicar el objetivo de la etapa'])

    def test_etapas_correcta(self):
        etapas_form_model = formset_factory(RetoEtapaForm, formset=EtapasFormSet,
                                            max_num=5)

        data = {
            # Etapas
            'form-INITIAL_FORMS': '0',
            'form-TOTAL_FORMS': '1',
            'form-MAX_NUM_FORM': '5',

            # 1º Etapa
            'form-0-objetivo_imagen': '',
            'form-0-objetivo_video': '',
            'form-0-objetivo_audio': '',
            'form-0-objetivo_texto': 'Objetivo 1º ETAPA',
        }

        etapas_form = etapas_form_model(data)

        self.assertEqual(len(etapas_form.errors[0]), 0)


##########################################################################################

# Comprobamos la validación del formulario de PRUEBA
class RetoPruebaTest(TestCase):

    def test_campos_vacios(self):
        data = {}
        form = PruebaForm(data)

        self.assertEqual(form.errors['prueba_texto'],
                         ['Debes indicar alguna prueba en la etapa'])

    def test_multiples_prueba(self):
        data = {
            'prueba_texto': 'Prueba prueba'
        }

        prueba_imagen = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        prueba_imagen = open(prueba_imagen, 'rb')

        form = PruebaForm(data=data, files={'prueba_imagen': SimpleUploadedFile(
            prueba_imagen.name, prueba_imagen.read())})

        self.assertEqual(form.errors['prueba_texto'],
                         ['Elige una forma de indicar la prueba de la etapa'])

    def test_prueba_correcta(self):
        data = {
            'prueba_texto': 'Objetivo prueba',
            'prueba_imagen': '',
            'prueba_audio': '',
            'prueba_video': ''
        }

        form = PruebaForm(data=data)

        self.assertEqual(len(form.errors), 0)


##########################################################################################

# Comprobamos la validación del formulario de ÁNIMOS
class RetoAnimoTest(TestCase):

    def test_campos_vacios(self):
        data = {}
        form = AnimoForm(data)

        self.assertEqual(form.errors['animo_texto'],
                         ['Debes indicar algún mensaje de ánimo en la etapa'])

    def test_multiples_prueba(self):
        data = {
            'animo_texto': 'Prueba ánimo'
        }

        animo_imagen = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        animo_imagen = open(animo_imagen, 'rb')

        form = AnimoForm(data=data, files={'animo_imagen': SimpleUploadedFile(
            animo_imagen.name, animo_imagen.read())})

        self.assertEqual(form.errors['animo_texto'],
                         ['Elige una forma de animar en la etapa'])

    def test_animo_correcto(self):
        data = {
            'animo_texto': 'Objetivo ánimo',
            'animo_imagen': '',
            'animo_audio': '',
            'animo_video': ''
        }

        form = AnimoForm(data=data)

        self.assertEqual(len(form.errors), 0)


##########################################################################################

# Comprobamos la validación del EDITAR PERFIL
class PerfilTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario.objects.create_user(email="editar_perfil@forms.com", nombre="María Jesús",
                                    password="Password1.",
                                    clave_aleatoria="clave1",
                                    clave_fija="clave2",
                                    foto_perfil="/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg")

    def test_correcto(self):
        form_data = {
            'email': 'editar_perfil@forms.com',
            'nombre': 'María Jesús',
            'password_antigua': 'Password1.',
            'password_nueva': 'Password1*',
            'password_again': 'Password1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = PerfilForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(len(form.errors), 0)

    def test_nombre_largo(self):
        form_data = {
            'email': 'editar_perfil@forms.com',
            'nombre': 'María Jesús López Salmerón María Jesús López Salmerón María '
                      'Jesús López Salmerón María Jesús López Salmerón',
            'password_antigua': 'Password1.',
            'password_nueva': 'Password1*',
            'password_again': 'Password1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = PerfilForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['nombre'], ["Asegúrese de que este valor tenga "
                                                 "menos de 100 caracteres (tiene 107)."])

    def test_no_antigua_password(self):
        form_data = {
            'email': 'editar_perfil@forms.com',
            'nombre': 'María Jesús',
            'password_antigua': 'Password1!',
            'password_nueva': 'Password1*',
            'password_again': 'Password1',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = PerfilForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['password_antigua'],
                         ['La contraseña no es la esperada'])

    def test_no_coinciden_password(self):
        form_data = {
            'email': 'editar_perfil@forms.com',
            'nombre': 'María Jesús',
            'password_antigua': 'Password1.',
            'password_nueva': 'Password1*',
            'password_again': 'Password1',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = PerfilForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['password_again'], ['Las contraseñas deben ser '
                                                         'iguales'])

    def test_password_no_numerico(self):
        form_data = {
            'email': 'editar_perfil@forms.com',
            'nombre': 'María Jesús',
            'password_antigua': 'Password1.',
            'password_nueva': 'Password*',
            'password_again': 'Password*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = PerfilForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['password_nueva'], ['La contraseña debe contener '
                                                         'al menos un número'])

    def test_password_no_mayuscula(self):
        form_data = {
            'email': 'editar_perfil@forms.com',
            'nombre': 'María Jesús',
            'password_antigua': 'Password1.',
            'password_nueva': 'password1*',
            'password_again': 'password1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = PerfilForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['password_nueva'], ['La contraseña debe tener al '
                                                         'menos una mayúscula'])

    def test_password_no_simbolos(self):
        form_data = {
            'email': 'editar_perfil@forms.com',
            'nombre': 'María Jesús',
            'password_antigua': 'Password1.',
            'password_nueva': 'Password1',
            'password_again': 'Password1',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = PerfilForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['password_nueva'], ["La contraseña debe tener al "
                                                         "menos uno de estos símbolos: ("
                                                         ")[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"])

    def test_password_no_minuscula(self):
        form_data = {
            'email': 'editar_perfil@forms.com',
            'nombre': 'María Jesús',
            'password_antigua': 'Password1.',
            'password_nueva': 'PASSWORD1*',
            'password_again': 'PASSWORD1*',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/mariajesus@gmail.com.jpg"
        foto_perfil = open(foto_perfil, 'rb')

        form = PerfilForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['password_nueva'],
                         ["La contraseña debe contener al menos una letra "
                          "en minúscula"])

    def test_foto_de_perfil_vacio(self):
        form_data = {
            'email': 'editar_perfil@forms.com',
            'nombre': 'María Jesús',
            'password_antigua': 'Password1.',
            'password_nueva': 'Password1*',
            'password_again': 'Password1*',
        }

        form = PerfilForm(data=form_data)

        self.assertEqual(form.errors['foto_de_perfil'], ['Este campo es obligatorio.'])

    def test_imagen_vacia(self):
        form_data = {
            'email': 'editar_perfil@forms.com',
            'nombre': 'María Jesús',
            'password_antigua': 'Password1.',
            'password_nueva': 'Password1*',
            'password_again': 'Password1',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/prueba.txt"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['foto_de_perfil'],
                         ['El fichero enviado está vacío.'])

    def test_no_imagen(self):
        form_data = {
            'email': 'editar_perfil@forms.com',
            'nombre': 'María Jesús',
            'password_antigua': 'Password1.',
            'password_nueva': 'Password1*',
            'password_again': 'Password1',
        }

        foto_perfil = f"{BASE_DIR}/media/YoPuedo/foto_perfil/prueba2.txt"
        foto_perfil = open(foto_perfil, 'rb')

        form = RegistroForm(data=form_data, files={'foto_de_perfil': SimpleUploadedFile(
            foto_perfil.name, foto_perfil.read())})

        self.assertEqual(form.errors['foto_de_perfil'], ['Envíe una imagen válida. El '
                                                         'fichero que ha enviado no era '
                                                         'una imagen o se trataba de una '
                                                         'imagen corrupta.'])
