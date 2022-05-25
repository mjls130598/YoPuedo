from django.db import models


# TABLA MisRetos_usuario
class Usuario(models.Model):
    email = models.EmailField(primary_key=True)
    nombre = models.CharField(max_length=200)
    password = models.CharField(max_length=16)
    fotoPerfil = models.CharField(max_length=100)


# TABLA MisRetos_amistad
class Amistad(models.Model):
    amigo = models.ManyToManyRel(Usuario)
    otro_amigo = models.ManyToManyRel(Usuario)


# TABLA MisRetos_reto
class Reto(models.Model):
    id_reto = models.CharField(max_length=50, primary_key=True)
    objetivo = models.CharField(max_length=500)
    recompensa = models.CharField(max_length=500)
    estado = models.CharField(max_length=10, default="Propuesto")
    categoria = models.CharField(max_length=15)
    coordinador = models.ManyToOneRel(Usuario)


# TABLA MisRetos_participante:
class Participante(models.Model):
    email = models.ManyToManyRel(Usuario)
    id_reto = models.ManyToManyRel(Reto)


# TABLA MisRetos_animador:
class Animador(models.Model):
    email = models.ManyToManyRel(Usuario)
    id_reto = models.ManyToManyRel(Reto)
    superanimador = models.BooleanField(default=False)


# TABLA MisRetos_etapa
class Etapa(models.Model):
    id_etapa = models.CharField(max_length=50, primary_key=True)
    id_reto = models.ManyToOneRel(Reto)
    objetivo = models.CharField(max_length=500)
    estado = models.CharField(max_length=10, default="Propuesto")


# TABLA MisRetos_animo
class Animo(models.Model):
    id_etapa = models.ManyToManyRel(Etapa)
    animador = models.ManyToManyRel(Animador)
    mensaje = models.CharField(max_length=500)


# TABLA MisRetos_prueba
class Prueba(models.Model):
    id_etapa = models.ManyToManyRel(Etapa)
    animador = models.ManyToManyRel(Animador)
    prueba = models.CharField(max_length=500)


# TABLA MisRetos_calificacion
class Calificacion(models.Model):
    id_etapa = models.ManyToManyRel(Etapa)
    animador = models.ManyToManyRel(Animador)
    prueba = models.CharField(max_length=500)


# TABLA MisRetos_notificacion:
class Notificacion(models.Model):
    id_notificacion = models.CharField(max_length=50, primary_key=True)
    mensaje = models.CharField(max_length=500)
    categoria = models.CharField(max_length=15)
    estado = models.CharField(max_length=10, default="Recibido")
    usuario = models.ManyToOneRel(Usuario)