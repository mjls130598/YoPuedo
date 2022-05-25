# Herramientas
Las herramientas que utilizaremos para la construcción y el despliegue de la aplicación *Mis Retos* son las que se comentan a continuación:

## Django
[Django](https://www.djangoproject.com/) es un framework de alto nivel, escrito principalmente para Python, que se encarga de ayudar a los desarrolladores a la hora de crear aplicaciones web incluyendo diversos paquetes y middleware.

## MySQL
Utilizaremos para el almacenamiento y las consultas dentro de la base de datos una de tipo relacional por las siguientes razones:
* Para poder realizar consultas más complejas (por ejemplo, de tipo JOIN).
* Para crear claves extranjeras (foreign keys) entre distintas tablas y poder realizar el borrado en cascada fácilmente.

## pythonanywhere.com
La herramienta [pythonanywhere.com](https://www.pythonanywhere.com/) es un servidor exclusivo para proyectos escritos en Python donde lanzaremos el proyecto para que pueda ser accesible a través de cualquier dispositivo sin tener ninguna dependencia de donde se encuentre el proyecto almacenado localmente.

En ella, además de estar almacenado el código de la aplicación y de lanzar el proyecto a la web (en este caso se encontrará en [mariajesuslopez.pythonanywhere.com](http://mariajesuslopez.pythonanywhere.com/)), podremos crear la base de datos MySQL donde se almacenará y se consultará la información necesaria para la app.

Dentro del servidor, tenemos dos consolas: una para lanzar el proyecto y otra para consultar dentro del servidor la base de datos creada.
