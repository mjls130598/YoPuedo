# Memoria del proyecto

## Herramientas
Las herramientas que utilizaremos para la construcción y el despliegue de la 
aplicación *Mis Retos* son las que se comentan a continuación:

* [**Django**](https://www.djangoproject.com/) es un framework de alto nivel, 
escrito principalmente para Python, que se encarga de ayudar a los 
desarrolladores a la hora de crear aplicaciones web incluyendo diversos 
paquetes y middleware.

* **MySQL** lo utilizaremos para el almacenamiento y las consultas dentro de 
  la base de datos una de tipo relacional por las siguientes razones:
  * Para poder realizar consultas más complejas (por ejemplo, de tipo JOIN).
  * Para crear claves extranjeras (foreign keys) entre distintas tablas y 
    poder realizar el borrado en cascada fácilmente.

* [**pythonanywhere.com**](https://www.pythonanywhere.com/) es un 
servidor exclusivo para proyectos escritos en Python donde lanzaremos el 
proyecto para que pueda ser accesible a través de cualquier dispositivo sin 
tener ninguna dependencia de donde se encuentre el proyecto almacenado localmente. 
En ella, además de estar almacenado el código de la aplicación y de lanzar 
el proyecto a la web (en este caso se encontrará en [mariajesuslopez.
pythonanywhere.com](http://mariajesuslopez.pythonanywhere.com/)), podremos 
crear la base de datos MySQL donde se almacenará y se consultará la 
información necesaria para la app. Dentro del servidor, tenemos dos 
  consolas: una para lanzar el proyecto y otra para consultar dentro del 
  servidor la base de datos creada.

* [**Bootstrap**](https://getbootstrap.com/) biblioteca de templates para generar páginas 
  "responsive" para distintos tamaños de pantalla.

## Base de datos

### Instalaciones previas
Como hemos dicho anteriormente, vamos a manejar los datos de nuestra 
aplicación a través de *MySQL*. Entonces, para poder utilizar una base de 
datos _MySQL_ dentro de un proyecto de _Django_, debemos instalar en el 
entorno de *Python* el paquete **_pymysql_**. Nosotros lo instalamos en 
nuestro proyecto incluyendo dicho paquete dentro del fichero [requirements.txt](https://github.com/mjls130598/MisRetos/blob/master/requirements.txt).

Dentro del servidor *pythonanywhere*, creamos la base de datos que vamos a 
utilizar. En este caso hemos creado una cuyo nombre es **_mariajesuslopez$MISRETOS_**. 

### Configuración del proyecto
Una vez instalada la herramienta con la que se harán las consultas y se 
almacenarán los datos de la aplicación, dentro del proyecto haremos los 
siguientes cambios:

* Escribiremos la configuración de la base de datos dentro de un fichero 
  para su utilización dentro de la construcción de la aplicación. En el 
  archivo ```TFM/conf/db.mysql``` nos encontraremos con la siguiente información:
```commandline
# TFM/conf/db.mysql

[client]
database = mariajesuslopez$MISRETOS                         # Base de datos
user = mariajesuslopez                                      # Usuario
password = XXXXXXXXXX                                       # Contraseña
host = mariajesuslopez.mysql.pythonanywhere-services.com    # Servidor
default-character-set = utf8                                # Tipo de caracteres
```
* En [settings.py](https://github.com/mjls130598/MisRetos/blob/master/TFM/TFM/settings.py), insertamos las 
  siguientes líneas de código para que coja el fichero de configuración 
  anterior y el tipo de base de datos que vamos a utilizar:
```commandline
# TFM/TFM/settings.py

  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, 'conf/db.mysql'),
        }
    }
}
 ```

### Tablas (o modelos)

Ya realizadas las instalaciones y configuraciones correspondientes a la base 
de datos, procedemos a crear las tablas junto a sus tuplas correspondientes. 
Para ello, *Django* solamente necesitamos escribir dichas tablas en el 
fichero [models.py](https://github.com/mjls130598/MisRetos/blob/master/TFM/MisRetos/models.py) a través de la 
creación de clases con sus correspondientes atributos.

Como hacemos cuando creamos una tabla con MySQL, en cada tupla indicamos el 
tipo de dato a insertar, el máximo número de caracteres que puede guardar, 
si es una clave externa (foreign key) y/o una clave primaria. Para aquellas 
tuplas que tienen una relación N:M utilizamos el tipo de modelo 
**_ManyToMany_**, y si es una relación 1:1, usamos **_ForeignKey_**.

En el caso de la tabla **_Amistad_**, al ser dos claves primarias de la 
misma tabla, hemos tenido que poner un "nombre" para que *Django* pueda 
diferenciar las dos columnas (mediante el atributo *related_name*):

```python
# TABLA MisRetos_amistad

class Amistad(models.Model):
    amigo = models.ManyToManyField(Usuario, related_name="amigo")
    otro_amigo = models.ManyToManyField(Usuario, related_name="otro_Amigo")
```

Una vez escritas las clases que formarán parte del manejo de datos del 
proyecto, debemos lanzar las siguientes líneas de código para que se guarden 
y se generen las tablas en la base de datos:

```commandline
python manage.py makemigrations
python manage.py migrate
```

## Templates

Como hemos dicho en el apartado de *Herramientas*, vamos a utilizar la 
biblioteca de *Boostrap* para no generar de cero la visualización de las 
páginas. 

Para que funcione dentro de nuestro proyecto de *Django*, hay que realizar 
los siguientes pasos:

1. Instalar el paquete *django-bootstrap-v5*. Nosotras lo tenemos añadido 
   dentro del archivo de paquetes requeridos ([requirements.txt](https://github.com/mjls130598/MisRetos/blob/master/requirements.txt)).
2. Dentro del archivo [settings.py](https://github.com/mjls130598/MisRetos/blob/master/TFM/TFM/settings.py) incluiremos en 
   el apartado de *INSTALLED_APPS* el paquete *bootstrap5*.