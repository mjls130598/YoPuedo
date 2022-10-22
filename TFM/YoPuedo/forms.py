import logging
import re
from django import forms
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

# Formulario de petición de claves
class RetoGeneralForm(forms.Form):
    titulo = forms.CharField(label='Título: ', max_length='500',
                             min_length='10', widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }))
    objetivo_imagen = forms.ImageField(label="Subir foto",
                                       widget=forms.ClearableFileInput(
                                           attrs={
                                               'class': 'form-control uploadfile'
                                           }))
    objetivo_audio = forms.FileField(label="Subir audio",
                                     widget=forms.ClearableFileInput(
                                         attrs={
                                             'class': 'form-control uploadfile',
                                             'accept': "audio/*"
                                         }))
    objetivo_video = forms.FileField(label="Subir vídeo",
                                     widget=forms.ClearableFileInput(
                                         attrs={
                                             'class': 'form-control uploadfile',
                                             'accept': "video/*"
                                         }))

    objetivo_texto = forms.CharField(max_length='500', widget=forms.Textarea(
        attrs={
            'class': 'form-control mt-2 mb-2',
            'placeholder': 'O escribe el objetivo ...',
            'rows': '2'
        }))

    categoria = forms.ChoiceField(label="Categoría: ", choices=Utils.CATEGORIAS_CHOOSE)

    recompensa_imagen = forms.ImageField(label="Subir foto",
                                         widget=forms.ClearableFileInput(
                                             attrs={
                                                 'class': 'form-control uploadfile'
                                             }))
    recompensa_audio = forms.FileField(label="Subir audio",
                                       widget=forms.ClearableFileInput(
                                           attrs={
                                               'class': 'form-control uploadfile',
                                               'accept': "audio/*"
                                           }))
    recompensa_video = forms.FileField(label="Subir vídeo",
                                       widget=forms.ClearableFileInput(
                                           attrs={
                                               'class': 'form-control uploadfile',
                                               'accept': "video/*"
                                           }))

    recompensa_texto = forms.CharField(max_length='500', widget=forms.Textarea(
        attrs={
            'class': 'form-control mt-2 mb-2',
            'placeholder': 'O escribe la recompensa ...',
            'rows': '2'
        }))
