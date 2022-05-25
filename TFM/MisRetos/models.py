from django.db import models


# TABLA MisRetos_usuario
class Usuario(models.Model):
    email = models.EmailField(primary_key=True)
    nombre = models.CharField(max_length=200)
    password = models.CharField(max_length=16)
    fotoPerfil = models.CharField(max_length=100)


# TABLA MisRetos_amistad
class Amistad(models.Model):
    amigo = models.ManyToManyRel(Usuario, on_delete=models.CASCADE, related_name='amigo', primary_key=True)
    otro_amigo = models.ManyToManyRel(Usuario, on_delete=models.CASCADE, related_name='otro_amigo', primary_key=True)

    class Meta:
        unique_together = (('amigo', 'otro_amigo'),)


# TABLA MisRetos_reto
class Reto(models.Model):
    id_reto = models.CharField(max_length=50, primary_key=True)
    objetivo = models.CharField(max_length=500)
    recompensa = models.CharField(max_length=500)
    estado = models.CharField(max_length=10, default="Propuesto")
    categoria = models.CharField(max_length=15)
    coordinador = models.ManyToOneRel(Usuario, on_delete=models.CASCADE, db_column="email")


# TABLA MisRetos_participante:
class Participante(models.Model):
    email = models.ManyToManyRel(Usuario, on_delete=models.CASCADE, db_column="email", primary_key=True)
    id_reto = models.ManyToManyRel(Reto, on_delete=models.CASCADE, db_column="id_reto", primary_key=True)

    class Meta:
        unique_together = (('email', 'id_reto'),)


# TABLA MisRetos_animador:
class Animador(models.Model):
    email = models.ManyToManyRel(Usuario, on_delete=models.CASCADE, db_column="email", primary_key=True)
    id_reto = models.ManyToManyRel(Reto, on_delete=models.CASCADE, db_column="id_reto", primary_key=True)
    superanimador = models.BooleanField(default=False)

    class Meta:
        unique_together = (('email', 'id_reto'),)


# TABLA MisRetos_etapa
class Etapa(models.Model):
    id_etapa = models.CharField(max_length=50, primary_key=True)
    id_reto = models.ManyToOneRel(Reto, on_delete=models.CASCADE, db_column="id_reto")
    objetivo = models.CharField(max_length=500)
    estado = models.CharField(max_length=10, default="Propuesto")


# TABLA MisRetos_animo
class Animo(models.Model):
    id_etapa = models.ManyToManyRel(Etapa, on_delete=models.CASCADE, db_column="id_etapa")
    animador = models.ManyToManyRel(Animador, on_delete=models.CASCADE, db_column="email")
    mensaje = models.CharField(max_length=500)


# TABLA MisRetos_prueba
class Prueba(models.Model):
    id_etapa = models.ManyToManyRel(Etapa, on_delete=models.CASCADE, db_column="id_etapa")
    animador = models.ManyToManyRel(Animador, on_delete=models.CASCADE, db_column="email")
    prueba = models.CharField(max_length=500)


# TABLA MisRetos_calificacion
class Calificacion(models.Model):
    id_etapa = models.ManyToManyRel(Etapa, on_delete=models.CASCADE, db_column="id_etapa", primary_key=True)
    animador = models.ManyToManyRel(Animador, on_delete=models.CASCADE, db_column="email", primary_key=True)
    prueba = models.CharField(max_length=500)

    class Meta:
        unique_together = (('id_etapa', 'animador'),)


# TABLA MisRetos_notificacion:
class Notificacion(models.Model):
    id_notificacion = models.CharField(max_length=50, primary_key=True)
    mensaje = models.CharField(max_length=500)
    categoria = models.CharField(max_length=15)
    estado = models.CharField(max_length=10, default="Recibido")
    usuario = models.ManyToOneRel(Usuario, on_delete=models.CASCADE, db_column="email")