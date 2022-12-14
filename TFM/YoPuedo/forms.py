import logging
import re
from django import forms
from django.forms import BaseFormSet

from .models import Usuario

from .utils import Utils

logger = logging.getLogger(__name__)


##########################################################################################

# Formulario de registro
class RegistroForm(forms.Form):
    email = forms.EmailField(label='Email:',
                             widget=forms.EmailInput(
                                 attrs={
                                     'class': 'form-control',
                                     'placeholder': 'ejemplo@ejemplo.com',
                                 }))
    nombre = forms.CharField(label='Nombre:', max_length='100',
                             widget=forms.TextInput(
                                 attrs={
                                     'class': 'form-control',
                                     'placeholder': 'María Jesús López'
                                 }))
    password = forms.CharField(label='Contraseña:', max_length='16', min_length='8',
                               widget=forms.PasswordInput(
                                   attrs={
                                       'class': 'form-control'
                                   }))
    password_again = forms.CharField(label='Repetir contraseña:', max_length='16',
                                     min_length='8', widget=forms.PasswordInput(
            attrs={
                'class': 'form-control col-10'
            }))
    foto_de_perfil = forms.ImageField(label='Foto de perfil:',
                                      widget=forms.ClearableFileInput(
                                          attrs={
                                              'class': 'form-control'
                                          }))

    def clean(self):
        logger.info("Checkeando registro")

        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password_again')

        if password != password2:
            logger.error("Las contraseñas introducidas no son iguales")
            self.add_error('password_again', "Las contraseñas deben ser iguales")

        if not re.findall('\d', password):
            logger.error("La contraseña no contiene números")
            self.add_error('password', "La contraseña debe contener al menos un número")

        if not re.findall('[A-Z]', password):
            logger.error("La contraseña no tiene ninguna mayúscula")
            self.add_error('password', "La contraseña debe tener al menos una mayúscula")

        if not re.findall('[a-z]', password):
            logger.error("La contraseña no tiene ninguna minúscula")
            self.add_error('password', "La contraseña debe contener al menos una letra "
                                       "en minúscula")

        if not re.findall('[()\[\]{}|\\`~!@#$%^&\*_\-\+=;:\'",<>./\?]', password):
            logger.error("La contraseña no contiene ningún símbolo")
            self.add_error('password', "La contraseña debe tener al menos uno de estos "
                                       "símbolos: "
                                       "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?")

        email = cleaned_data.get('email')

        if Usuario.objects.filter(email=email).exists():
            logger.error("Ya existe un usuario con ese email")
            self.add_error('email', "Ya existe una cuenta con ese email. Pruebe con "
                                    "otro.")

        return self


##########################################################################################

# Formulario de inicio sesión
class InicioForm(forms.Form):
    email_sesion = forms.EmailField(label='Email:',
                                    widget=forms.EmailInput(
                                        attrs={
                                            'class': 'form-control',
                                            'placeholder': 'ejemplo@ejemplo.com',
                                        }))
    password_sesion = forms.CharField(label='Contraseña:', max_length='16',
                                      min_length='8',
                                      widget=forms.PasswordInput(
                                          attrs={
                                              'class': 'form-control'
                                          }))

    def clean(self):
        logger.info("Checkeando inicio")

        cleaned_data = super().clean()

        email = cleaned_data.get('email_sesion')

        if not Usuario.objects.filter(email=email).exists():
            logger.error("No existe un usuario con ese email")
            self.add_error('password_sesion', "Usuario y/o contraseña incorrect@")

        else:
            password = cleaned_data.get('password_sesion')
            usuario = Usuario.objects.get(email=email)
            if not usuario.check_password(password):
                logger.error("Contraseña incorrecta")
                self.add_error('password_sesion', "Usuario y/o contraseña incorrect@")

        return self


##########################################################################################

# Formulario de petición de claves
class ClaveForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    contador = forms.IntegerField(widget=forms.HiddenInput())
    clave = forms.CharField(label='Código de verificación:', max_length='16',
                            min_length='10', widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }))

    def clean(self):
        logger.info("Checkeando petición clave")

        cleaned_data = super().clean()

        email = cleaned_data.get('email')
        usuario = Usuario.objects.get(email=email)

        clave = cleaned_data.get('clave')

        if usuario.clave_fija != clave and usuario.clave_aleatoria != clave:
            logger.error("Las claves no coinciden con la introducida")
            self.add_error('clave', 'La clave introducida es incorrecta. Por favor, '
                                    'introdúcela de nuevo.')

        return self


##########################################################################################

# Formulario de reto GENERAL
class RetoGeneralForm(forms.Form):
    titulo = forms.CharField(label='Título: ', max_length='500',
                             min_length='10', widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }), required=False)
    objetivo_imagen = forms.ImageField(label="Subir foto",
                                       widget=forms.ClearableFileInput(
                                           attrs={
                                               'class': 'form-control uploadfile'
                                           }),
                                       required=False)
    objetivo_audio = forms.FileField(label="Subir audio",
                                     widget=forms.ClearableFileInput(
                                         attrs={
                                             'class': 'form-control uploadfile',
                                             'accept': "audio/*"
                                         }),
                                     required=False)
    objetivo_video = forms.FileField(label="Subir vídeo",
                                     widget=forms.ClearableFileInput(
                                         attrs={
                                             'class': 'form-control uploadfile',
                                             'accept': "video/*"
                                         }),
                                     required=False)

    objetivo_texto = forms.CharField(max_length='500', widget=forms.Textarea(
        attrs={
            'class': 'form-control mt-2 mb-2',
            'placeholder': 'O escribe el objetivo ...',
            'rows': '2'
        }), required=False)

    categoria = forms.ChoiceField(label="Categoría: ", choices=Utils.CATEGORIAS_CHOOSE,
                                  widget=forms.Select(
                                      attrs={
                                          'class': 'col'
                                      }), required=False)

    recompensa_imagen = forms.ImageField(label="Subir foto",
                                         widget=forms.ClearableFileInput(
                                             attrs={
                                                 'class': 'form-control uploadfile'
                                             }),
                                         required=False)
    recompensa_audio = forms.FileField(label="Subir audio",
                                       widget=forms.ClearableFileInput(
                                           attrs={
                                               'class': 'form-control uploadfile',
                                               'accept': "audio/*"
                                           }),
                                       required=False)
    recompensa_video = forms.FileField(label="Subir vídeo",
                                       widget=forms.ClearableFileInput(
                                           attrs={
                                               'class': 'form-control uploadfile',
                                               'accept': "video/*"
                                           }),
                                       required=False)

    recompensa_texto = forms.CharField(max_length='500', widget=forms.Textarea(
        attrs={
            'class': 'form-control mt-2 mb-2',
            'placeholder': 'O escribe la recompensa ...',
            'rows': '2'
        }), required=False)

    def clean(self):
        logger.info("Checkeando nuevo reto - General")

        cleaned_data = super().clean()

        objetivo_texto = cleaned_data.get('objetivo_texto')
        objetivo_imagen = cleaned_data.get('objetivo_imagen')
        objetivo_audio = cleaned_data.get('objetivo_audio')
        objetivo_video = cleaned_data.get('objetivo_video')

        recompensa_texto = cleaned_data.get('recompensa_texto')
        recompensa_imagen = cleaned_data.get('recompensa_imagen')
        recompensa_audio = cleaned_data.get('recompensa_audio')
        recompensa_video = cleaned_data.get('recompensa_video')

        categoria = cleaned_data.get('categoria')
        titulo = cleaned_data.get('titulo')

        if not titulo:
            logger.error("No se ha indicado el título del reto")
            self.add_error('titulo', 'Debes indicar el título del reto')

        if len(titulo) < 10 or len(titulo) > 500:
            logger.error("El título demasiado largo o corto")
            self.add_error('titulo', 'Debes escribir entre 10 y 500 caracteres')

        if not objetivo_texto and not objetivo_imagen and not objetivo_video and not \
                objetivo_audio:
            logger.error("No se ha indicado el objetivo")
            self.add_error('objetivo_texto', 'Debes indicar el objetivo del reto')

        if Utils.numero_elementos_importados([objetivo_texto, objetivo_audio,
                                              objetivo_video, objetivo_imagen]) > 1:
            logger.error("Se ha introducido varias maneras en objetivo")
            self.add_error('objetivo_texto', 'Elige una forma de indicar el objetivo '
                                             'del reto')

        if not recompensa_texto and not recompensa_imagen and not recompensa_audio and \
                not recompensa_video:
            logger.error("No se ha indicado la recompensa")
            self.add_error('recompensa_texto', 'Debes indicar la recompensa del reto')

        if Utils.numero_elementos_importados([recompensa_texto, recompensa_video,
                                              recompensa_audio, recompensa_imagen]) > 1:
            logger.error("Se ha introducido varias maneras en recompensa")
            self.add_error('recompensa_texto', 'Elige una forma de indicar la recompensa '
                                               'del reto')

        if categoria == "":
            logger.error("No ha seleccionado una categoría")
            self.add_error('categoria', 'Debes indicar qué tipo de categoría es el reto')

        return self


##########################################################################################

# Formulario de reto ETAPAS
class RetoEtapaForm(forms.Form):
    objetivo_imagen = forms.ImageField(label="Subir foto",
                                       widget=forms.ClearableFileInput(
                                           attrs={
                                               'class': 'form-control uploadfile'
                                           }),
                                       required=False)
    objetivo_audio = forms.FileField(label="Subir audio",
                                     widget=forms.ClearableFileInput(
                                         attrs={
                                             'class': 'form-control uploadfile',
                                             'accept': "audio/*"
                                         }),
                                     required=False)
    objetivo_video = forms.FileField(label="Subir vídeo",
                                     widget=forms.ClearableFileInput(
                                         attrs={
                                             'class': 'form-control uploadfile',
                                             'accept': "video/*"
                                         }),
                                     required=False)

    objetivo_texto = forms.CharField(max_length='500', widget=forms.Textarea(
        attrs={
            'class': 'form-control mt-2 mb-2',
            'placeholder': 'O escribe el objetivo ...',
            'rows': '5'
        }), required=False)

    def clean(self):
        logger.info("Checkeando nuevo reto - Etapa")

        cleaned_data = super().clean()

        objetivo_texto = cleaned_data.get('objetivo_texto')
        objetivo_imagen = cleaned_data.get('objetivo_imagen')
        objetivo_audio = cleaned_data.get('objetivo_audio')
        objetivo_video = cleaned_data.get('objetivo_video')

        if not objetivo_texto and not objetivo_imagen and not objetivo_video and not \
                objetivo_audio:
            logger.error("No se ha indicado el objetivo")
            self.add_error('objetivo_texto', 'Debes indicar el objetivo de la etapa')

        if Utils.numero_elementos_importados([objetivo_texto, objetivo_audio,
                                              objetivo_video, objetivo_imagen]) > 1:
            logger.error("Se ha introducido varias maneras en objetivo")
            self.add_error('objetivo_texto', 'Elige una forma de indicar el objetivo '
                                             'de la etapa')

        return self


##########################################################################################

# Formulario de grupo de ETAPAS
class EtapasFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        for index in range(self.total_form_count()):

            logger.info(self.forms['index'])

            if not self.forms[index]:
                self.forms[index].clean()

            if self.can_delete and self._should_delete_form(self.forms[index]):
                continue

        return self


##########################################################################################

# Formulario de AMIGOS
class AmigosForm(forms.Form):
    consulta = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Buscar amigo ...'
        }), required=False)
    relacion = forms.CharField(widget=forms.HiddenInput())
