# Herramienta de Visualización y Manejo de Datos

## Descripción General

Este repositorio contiene una herramienta de visualización y manejo de datos financieros y operativos, diseñada específicamente para una pequeña empresa. La versión original se encuentra actualmente en uso, mientras que este repositorio muestra una versión de prueba/demostración.

## Extracción y Almacenamiento de Datos

La herramienta cuenta con las siguientes capacidades de manejo de datos:

- **Integración con Google Drive**: Utiliza Google Cloud APIs para extraer información directamente desde Google Drive, permitiendo un trabajo sincronizado y actualizado. (Para fines de demostración, esta versión genera datos simulados de manera local.)
- **Base de datos relacional**: Los datos se almacenan en un archivo `.DB` local en la app en Streamlit.io.

### Estructura de Datos

![Diagrama de estructura de datos](main/images/base_relacional.png)

*Nota: Reemplaza "ruta/a/tu/imagen.png" con la ubicación real de tu imagen*

## Despliegue

La herramienta está construida pensando en la accesibilidad y facilidad de uso:

- **Plataforma**: Desarrollada en Streamlit, lo que permite:
  - Despliegue gratuito y sin complicaciones
  - Acceso multi-dispositivo (computadoras, tablets, móviles)
  - Interfaz limpia y responsiva

### Acceso a la Demo

Puedes acceder a la versión de prueba aquí:  
🔗 [https://d2caps-inicio.streamlit.app/](https://d2caps-inicio.streamlit.app/)

**Nota**: Si la página está en modo de suspensión, simplemente presiona el botón para iniciar la aplicación. El proceso toma menos de 20 segundos.

## Tecnologías Utilizadas

- Streamlit
- Google Cloud APIs
- Base de datos SQLite (.DB)
