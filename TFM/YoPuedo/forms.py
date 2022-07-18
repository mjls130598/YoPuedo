import logging
import re
from django import forms
from .models import Usuario

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
            self.add_error('password_sesion', "Usuario y/o incorrecto")

        else:
            password = cleaned_data.get('password_sesion')
            usuario = Usuario.objects.get(email=email)
            if usuario.password != password:
                logger.error("Contraseña incorrecta")
                self.add_error('password_sesion', "Usuario y/o incorrecto")

        return self


##########################################################################################

# Formulario de petición de claves
class ClaveForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    tipo = forms.CharField(widget=forms.HiddenInput())
    contador = forms.IntegerField(widget=forms.HiddenInput())
    clave = forms.CharField(label='Código de verificación:', max_length='16',
                            widget=forms.TextInput(
                                attrs={
                                    'class': 'form-control'
                                }))

    def clean(self):
        logger.info("Comprobamos datos de petición de clave")

        cleaned_data = super.clean()
        email = cleaned_data.get('email')
        usuario = Usuario.objects.get(email=email)

        clave = cleaned_data.get('clave')

        if clave != usuario.clave_fija and clave != usuario.clave_aleatoria:
            logger.info("Clave introducida es errónea")
            self.add_error('clave', 'La clave introducida no es la correcta. ' +
                                    'Inténtelo de nuevo')
