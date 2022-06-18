from django import forms


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
    contraseña = forms.CharField(label='Contraseña:',
                                 widget=forms.PasswordInput(
                                     attrs={
                                         'class': 'form-control'
                                     }))
    repetir_contraseña = forms.CharField(label='Repetir contraseña:',
                                         widget=forms.PasswordInput(
                                             attrs={
                                                 'class': 'form-control'
                                             }))
    foto_de_perfil = forms.ImageField(label='Foto de perfil:',
                                      widget=forms.FileInput(
                                          attrs={
                                              'class': 'form-control'
                                          }))
