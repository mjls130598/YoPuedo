from django import forms
from . import utils


def upload_to(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class registro(forms.Form):
    email = forms.EmailField(label='Email:',
                             widget=forms.EmailInput(
                                 attrs={
                                     'class': 'form-control',
                                     'placeholder': 'ejemplo@ejemplo.com',
                                 }))
    nombre = forms.CharField(label='Nombre:', max_length='100',
                             widget=forms.TextInput(
                                 attrs={
                                     'class': 'form-control'
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
    foto_de_perfil = forms.FileField(label='Foto de perfil:',
                                     upload_to=upload_to,
                                     widget=forms.FileInput(
                                         attrs={
                                             'class': 'form-control'
                                         }))

    def clean(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password_again']
        foto_perfil = self['foto_de_perfil']

        if password != password2:
            self.add_error('repetir_contraseña', "Las constraseñas deben ser iguales")

        if not foto_perfil.filename:
            self.add_error('foto_de_perfil', "Hay un problema con ese archivo, "
                                             "utilice otro")

        if not utils.checkear_imagen(foto_perfil.filename):
            self.add_error('foto_de_perfil', 'El archivo dado no es una imagen')

        return self
