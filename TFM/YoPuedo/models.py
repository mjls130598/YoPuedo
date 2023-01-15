from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password, foto_perfil, clave_fija,
                    clave_aleatoria):
        usuario = self.model(email=email, nombre=nombre, password=password,
                             foto_perfil=foto_perfil, clave_fija=clave_fija,
                             clave_aleatoria=clave_aleatoria)
        usuario.set_password(password)
        usuario.is_superuser = False
        usuario.save(using=self._db)
        return usuario

    def get_by_natural_key(self, username):
        return self.get(email=username)


# TABLA YoPuedo_usuario
class Usuario(AbstractBaseUser):
    email = models.EmailField(primary_key=True)
    nombre = models.CharField(max_length=100)
    foto_perfil = models.CharField(max_length=200)
    clave_fija = models.CharField(max_length=16)
    clave_aleatoria = models.CharField(max_length=10)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'password', 'foto_perfil', 'clave_fija',
                       'clave_aleatoria']

    objects = UsuarioManager()

    def get_username(self):
        return self.email

    def natural_key(self):
        return self.email

    def update_clave(self, clave):
        self.clave_aleatoria = clave
        self.save()


# TABLA YoPuedo_amistad
class Amistad(models.Model):
    amigo = models.ManyToManyField(Usuario, related_name="amigo")
    otro_amigo = models.ManyToManyField(Usuario, related_name="otro_amigo")


# TABLA YoPuedo_reto
class Reto(models.Model):
    id_reto = models.CharField(max_length=50, primary_key=True)
    titulo = models.CharField(max_length=500)
    objetivo = models.CharField(max_length=500)
    recompensa = models.CharField(max_length=500)
    estado = models.CharField(max_length=10, default="Propuesto")
    categoria = models.CharField(max_length=15)
    coordinador = models.ForeignKey(Usuario, on_delete=models.CASCADE)


# TABLA YoPuedo_participante:
class Participante(models.Model):
    usuario = models.ManyToManyField(Usuario)
    reto = models.ManyToManyField(Reto)


# TABLA YoPuedo_animador:
class Animador(models.Model):
    usuario = models.ManyToManyField(Usuario)
    reto = models.ManyToManyField(Reto)
    superanimador = models.BooleanField(default=False)


# TABLA YoPuedo_etapa
class Etapa(models.Model):
    id_etapa = models.CharField(max_length=50, primary_key=True)
    reto = models.ForeignKey(Reto, on_delete=models.CASCADE)
    objetivo = models.CharField(max_length=500)
    estado = models.CharField(max_length=10, default="Propuesto")


# TABLA YoPuedo_animo
class Animo(models.Model):
    etapa = models.ManyToManyField(Etapa)
    animador = models.ManyToManyField(Animador)
    mensaje = models.CharField(max_length=500)


# TABLA YoPuedo_prueba
class Prueba(models.Model):
    etapa = models.ManyToManyField(Etapa)
    participante = models.ManyToManyField(Participante)
    prueba = models.CharField(max_length=500)


# TABLA YoPuedo_calificacion
class Calificacion(models.Model):
    etapa = models.ManyToManyField(Etapa)
    participante = models.ManyToManyField(Participante)
    calificacion = models.CharField(max_length=500)


# TABLA YoPuedo_notificacion:
class Notificacion(models.Model):
    id_notificacion = models.CharField(max_length=50, primary_key=True)
    mensaje = models.CharField(max_length=500)
    categoria = models.CharField(max_length=15)
    estado = models.CharField(max_length=10, default="Recibido")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
