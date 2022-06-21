import logging
from django import forms

logger = logging.getLogger(__name__)


class registro(forms.Form):
    email = forms.EmailField(label='Email:',
                             widget=forms.EmailInput(
                                 attrs={
                                     'placeholder': 'ejemplo@ejemplo.com',
                                 }))
    nombre = forms.CharField(label='Nombre:', max_length='100')
    password = forms.CharField(label='Contraseña:', max_length='16', min_length='8',
                               widget=forms.PasswordInput)
    password_again = forms.CharField(label='Repetir contraseña:', max_length='16',
                                     min_length='8', widget=forms.PasswordInput)
    foto_de_perfil = forms.ImageField(label='Foto de perfil:')

    def clean(self):

        logger.info("Checkeando registro")

        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password_again']

        if password != password2:
            logger.info("Las contraseñas introducidas no son iguales")
            self.add_error('password_again', "Las contraseñas deben ser iguales")

        return self
