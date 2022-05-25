from django.db import models


# TABLA MisRetos_usuario
class Usuario(models.Model):
    email = models.EmailField(primary_key=True)
    nombre = models.CharField(max_length=200)
    password = models.CharField(max_length=16)
    fotoPerfil = models.CharField(max_length=100)


# TABLA MisRetos_amistad
class Amistad(models.Model):
    amigo = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    otro_amigo = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('amigo', 'otro_amigo'),)


# TABLA MisRetos_reto
class Reto(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    objetivo = models.CharField(max_length=500)
    recompensa = models.CharField(max_length=500)
    estado = models.CharField(max_length=10, default="Propuesto")
    categoria = models.CharField(max_length=15)
    coordinador = models.ForeignKey(Usuario, on_delete=models.CASCADE)


# TABLA MisRetos_participante:
class Participante(models.Model):
    email = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id = models.ForeignKey(Reto, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('email', 'id'),)


# TABLA MisRetos_animador:
class Animador(models.Model):
    email = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id = models.ForeignKey(Reto, on_delete=models.CASCADE)
    superanimador = models.BooleanField(default=False)

    class Meta:
        unique_together = (('email', 'id'),)


# TABLA MisRetos_etapa
class Etapa(models.Model):
    id = models.CharField(max_length=50)
    id_reto = models.ForeignKey(Reto, on_delete=models.CASCADE)
    objetivo = models.CharField(max_length=500)
    estado = models.CharField(max_length=10, default="Propuesto")

    class Meta:
        unique_together = (('id_reto', 'id'),)


# TABLA MisRetos_animo
class Animo(models.Model):
    id = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    animador = models.ForeignKey(Animador, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=500)


# TABLA MisRetos_prueba
class Prueba(models.Model):
    id_etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    animador = models.ForeignKey(Animador, on_delete=models.CASCADE)
    prueba = models.CharField(max_length=500)


# TABLA MisRetos_calificacion
class Calificacion(models.Model):
    id_etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE)
    animador = models.ForeignKey(Animador, on_delete=models.CASCADE)
    prueba = models.CharField(max_length=500)

    class Meta:
        unique_together = (('id_etapa', 'animador'),)


# TABLA MisRetos_notificacion:
class Notificacion(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    mensaje = models.CharField(max_length=500)
    categoria = models.CharField(max_length=15)
    estado = models.CharField(max_length=10, default="Recibido")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)