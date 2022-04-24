# Sistema de detección de defectos en tablas de madera

Este es un trabajo para la asignatura Aplicaciones Industriales y Comerciales de la Visión Artificial, en el Master 
Universitario en Visión Artificial de la URJC.

[![Deployment](https://github.com/dmariaa/AIVA_2022_wooden_plank_defect_detector/actions/workflows/deployment.yml/badge.svg)](https://github.com/dmariaa/AIVA_2022_wooden_plank_defect_detector/actions/workflows/deployment.yml)

## Proyecto a desarrollar

En este proyecto se desarrollará un módulo para la detección de anomalías en tableros de madera. Este 
módulo estará preparado para integrarse dentro de los sistemas de un cliente que fabrica figuras y piezas de madera, 
y tiene como objetivo la detección de defectos (circulos, grietas, manchas...) en los tableros de madera,
previa a la proyección de la plantilla de corte que usan los sistemas de corte automático del cliente.

De esta forma se hace posible automatizar la proyección de la plantilla evitando los defectos, y
ahorrando costes de madera desperdiciada y/o piezas con defectos.

## Como desplegar y testear

Para deplegar y testear la última versión, tan solo hay que ejecutar el contenedor docker que contiene esta versión.

```
docker run -p 8080:8080 dmariaa/aiyc-defect-detector:v1.0.0
```

Una vez ejecutado, tan solo hay que abrir un navegador web y acceder a:

http://localhost:8080

## Como probar y modificar el código 

Clonar este repositorio. Crear la carpeta "models", descargar el modelo actual de google drive y copiarlo en esta carpeta:

https://drive.google.com/file/d/1leux1CMUnWyWtVcIaJ7kyMKs3c8WvA3K/view?usp=sharing

Hay que disponer de python 3.9.5 o superior. Se puede instalar un entorno virtual:

```
virtualenv -p {path al directio de python}/3.9/bin/python3 venv
source venv/bin/activate
```

Instalar los requerimientos del proyecto.

```
python -m pip install -r requirements.txt
```

Asegurarse de que el directorio actual está en el path de python.

```
export PYTHONPATH=.:$PYTHONPATH
```

Ejecutar el servidor

```
python -u src/server.py
```

Para probar con una imagen:

```
python -u tools/server_test.py -i <path a la imagen de prueba>
```

## Los modelos se encuentran en

https://urjc-my.sharepoint.com/:f:/g/personal/d_maria_2016_alumnos_urjc_es/Ehjcvg8zUqxHq0klAELnW58BL6_2VcvGACptPuaWdN7HGw?e=iIzfuH
