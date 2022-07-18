from django.db import models


# TABLA YoPuedo_usuario
class Usuario(models.Model):
    email = models.EmailField(primary_key=True)
    nombre = models.CharField(max_length=100)
    password = models.CharField(max_length=16)
    fotoPerfil = models.CharField(max_length=200)
    claveFija = models.CharField(max_length=16)
    claveAleatoria = models.CharField(max_length=10)

    USERNAME_FIELD = 'email'


# TABLA YoPuedo_amistad
class Amistad(models.Model):
    amigo = models.ManyToManyField(Usuario, related_name="amigo")
    otro_amigo = models.ManyToManyField(Usuario, related_name="otro_Amigo")


# TABLA YoPuedo_reto
class Reto(models.Model):
    id_reto = models.CharField(max_length=50, primary_key=True)
    objetivo = models.CharField(max_length=500)
    recompensa = models.CharField(max_length=500)
    estado = models.CharField(max_length=10, default="Propuesto")
    categoria = models.CharField(max_length=15)
    coordinador = models.ForeignKey(Usuario, on_delete=models.CASCADE)


# TABLA YoPuedo_participante:
class Participante(models.Model):
    email = models.ManyToManyField(Usuario)
    id_reto = models.ManyToManyField(Reto)


# TABLA YoPuedo_animador:
class Animador(models.Model):
    email = models.ManyToManyField(Usuario)
    id_reto = models.ManyToManyField(Reto)
    superanimador = models.BooleanField(default=False)


# TABLA YoPuedo_etapa
class Etapa(models.Model):
    id_etapa = models.CharField(max_length=50, primary_key=True)
    id_reto = models.ForeignKey(Reto, on_delete=models.CASCADE)
    objetivo = models.CharField(max_length=500)
    estado = models.CharField(max_length=10, default="Propuesto")


# TABLA YoPuedo_animo
class Animo(models.Model):
    id_etapa = models.ManyToManyField(Etapa)
    animador = models.ManyToManyField(Animador)
    mensaje = models.CharField(max_length=500)


# TABLA YoPuedo_prueba
class Prueba(models.Model):
    id_etapa = models.ManyToManyField(Etapa)
    animador = models.ManyToManyField(Animador)
    prueba = models.CharField(max_length=500)


# TABLA YoPuedo_calificacion
class Calificacion(models.Model):
    id_etapa = models.ManyToManyField(Etapa)
    animador = models.ManyToManyField(Animador)
    prueba = models.CharField(max_length=500)


# TABLA YoPuedo_notificacion:
class Notificacion(models.Model):
    id_notificacion = models.CharField(max_length=50, primary_key=True)
    mensaje = models.CharField(max_length=500)
    categoria = models.CharField(max_length=15)
    estado = models.CharField(max_length=10, default="Recibido")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)