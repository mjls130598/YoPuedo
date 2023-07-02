# ¡Yo puedo!

Proyecto realizado para el Trabajo de Fin de Máster de María Jesús López 
Salmerón del Máster Universitario de Ingeniería Informática de la 
Universisdad de Granada realizado durante el curso 2021/23.

## Descripción

*¡Yo puedo!* es una aplicación multidispositivo para que cualquier persona, 
sin importar sus discapacidades físicas o cognitivas, pueda crear y realizar 
cualquier tipo de reto. 
 
En cada reto puede dividirlo en cuantos pasos o etapas la persona desee, e 
incluso añadir evidencias y calificar cómo le ha ido en cada una de esas 
etapas para ver posteriormente cómo ha avanzado el reto.

Además, podemos añadir a nuestro grupo de amigos a los retos para que lo 
realicen junto a nosotros y/o para que nos ayuden a terminarlo mandándonos 
apoyo durante el proceso.

![Diagrama de arquitectura](Imágenes/Diagrama%20de%20arquitectura%20.png)

## Estructura del proyecto

La estructura que va a tener el proyecto que contenga la app *¡Yo puedo!* es 
la siguiente:

![Estructura de ficheros](Imágenes/Estructura%20de%20ficheros.png)

### Configuración del proyecto
Antes de lanzar el proyecto, hay que crear los archivos de configuración de 
las herramientas que necesita esta aplicación para ser utilizada en su 
totalidad.

En primer lugar, guardaremos dentro del archivo ```TFM/conf/.secret_key``` 
la clave secreta que se genera cuando creamos un proyecto en *Django*.

Posteriormente, escribiremos la configuración de la base de datos dentro de un 
fichero para su utilización dentro de la construcción de la aplicación. En el 
archivo ```TFM/conf/db.mysql``` nos encontraremos con la siguiente información:

```commandline
# TFM/conf/db.mysql

[client]
database = mariajesuslopez$YOPUEDO                          # Base de datos
user = mariajesuslopez                                      # Usuario
password = XXXXXXXXXX                                       # Contraseña
host = mariajesuslopez.mysql.pythonanywhere-services.com    # Servidor
default-character-set = utf8                                # Tipo de caracteres
```

Por último, crearemos la configuración necesaria para poder enviar 
correos electrónicos a través de la aplicación creada con *Django*. Dicha 
configuración la veremos implementada dentro del archivo ```TFM/conf/.email```
con la clave secreta que ofrece [*Gmail*](https://www.sitepoint.com/django-send-email/)
para utilizarse en la aplicación.

## Lanzamiento del proyecto

Este proyecto se encuentra disponible en la página web de [pythonanywhere.
com](http://mariajesuslopez.pythonanywhere.com/) para ver el funcionamiento 
de la aplicación *Mis Retos*.

Para lanzarlo localmente, en nuestro dispositivo tenemos que tener instalado 
los siguientes requerimientos:
* Python.
* MySQL (Una vez instalado, creamos la base de datos y el usuario con el que 
  accederemos a ella).

Una vez instaladas las aplicaciones anteriores, realizamos los siguientes pasos:

1. Descargamos el proyecto:
```commandline
git clone https://github.com/mjls130598/YoPuedo.git
```
2. Entramos en el repositorio:
```commandline
cd YoPuedo/
```
3. Instalamos los paquetes del proyecto:
```commandline
python -m pip install -r requirements.txt
```
4. Entramos en el proyecto:
```commandline
cd TFM/
```
5. Generamos las migraciones del proyecto:
```commandline
python manage.py makemigrations
python manage.py migrate
```
6. Lanzamos la aplicación:
```commandline
python manage.py runserver
```

Las investigaciones y los pasos realizados para el desarrollo de esta red 
social, lo podemos encontrar detalladamente dentro de la [memoria](Memoria%20TFM.pdf) de este 
proyecto.