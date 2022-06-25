import logging
import re
from django import forms
from .models import Usuario

logger = logging.getLogger(__name__)


class Registro(forms.Form):
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
                                                            'class': 'form-control'
                                                        }))
    foto_de_perfil = forms.ImageField(label='Foto de perfil:',
                                      widget=forms.ClearableFileInput(
                                          attrs={
                                              'class': 'form-control'
                                          }))

    def clean(self):
        logger.info("Checkeando registro")

        password = self['password']
        password2 = self['password_again']

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

        email = self.cleaned_data['email']

        if Usuario.objects.filter(email=email).exists():
            logger.error("Ya existe un usuario con ese email")
            self.add_error('email', "Ya existe una cuenta con ese email. Pruebe con "
                                    "otro.")

        return self
