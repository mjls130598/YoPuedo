# Mis Retos

Proyecto realizado para el Trabajo de Fin de Máster de María Jesús López 
Salmerón del Máster Universitario de Ingeniería Informática durante el curso 
2021/22.

## Descripción

*Mis Retos* es una aplicación multidispositivo para que cualquier persona, 
sin importar sus discapacidades físicas o cognitivas, pueda crear y realizar 
cualquier tipo de reto. 
 
En cada reto puede dividirlo en cuantos pasos o etapas la persona desee, e 
incluso añadir evidencias y calificar cómo le ha ido en cada una de esas 
etapas para ver posteriormente cómo ha avanzado el reto.

Además, podemos añadir a nuestro grupo de amigos a los retos para que lo 
realicen junto a nosotros y/o para que nos ayuden a terminarlo mandándonos 
apoyo durante el proceso.

## Estructura del proyecto

La estructura que va a tener el proyecto que contenga la app *Mis Retos* es 
la siguiente:

```commandline
	TFM/             # proyecto
	|
	├── conf
	│   ├── .secret_key           # la llave secreta del proyecto (setting.py)
	│   └── db.mysql              # configuración de la base de datos
	|
	├── MisRetos       # app
	│   ├── admin.py              # admininstración para la BD de app
	│   ├── apps.py               # configuración de la app
	│   ├── __init__.py           # package de la app
	│   ├── migrations            # migraciones realizadas
	│   │   └── __init__.py
	│   ├── models.py             # modelos (o tablas) de la app
	│   ├── tests.py              # tests de la app
	│   └── views.py              # controlador de la app
	|
	├── manage.py
	|
	├── static                    # directorio de archivos estáticos
	|
	└── TFM            # proyecto (datos de configuración)
	    ├── __init__.py           # package del proyecto
	    ├── settings.py           # Settings  del proyecto
	    ├── urls.py               # Mapeo de urls
	    └── wsgi.py               # Conexión  con el servidor web de producción
					
```

En el archivo [requirements.txt](https://github.com/mjls130598/MisRetos/blob/master/requirements.txt) estarán todos los paquetes necesarios para laconstrucción del proyecto

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
git clone https://github.com/mjls130598/MisRetos.git
```
2. Entramos en el repositorio:
```commandline
cd MisRetos/
```
3. Instalamos los paquetes del proyecto:
```commandline
python -m pip install -r requirements.txt
```
4. Entramos en el proyecto:
```commandline
cd TFM/
```
5. Modificamos la configuración de la base de datos en ```conf/db.mysql```.
6. Generamos las migraciones del proyecto:
```commandline
python manage.py makemigrations
python manage.py migrate
```
7. Lanzamos la aplicación:
```commandline
python manage.py runserver
```

La documentación del proyecto la encontramos dentro de la carpeta 
[Documentación](https://github.com/mjls130598/MisRetos/tree/master/Documentaci%C3%B3n)