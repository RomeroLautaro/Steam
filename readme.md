## Contexto

Tienes tu modelo de recomendación dando unas buenas métricas 😏, y ahora, cómo lo llevas al mundo real? 👀
El ciclo de vida de un proyecto de Machine Learning debe contemplar desde el tratamiento y recolección de los datos (Data Engineer stuff) hasta el entrenamiento y mantenimiento del modelo de ML según llegan nuevos datos.

## Datos de Steam

* **australian_user_reviews.json** contiene los comentarios que los usuarios realizaron sobre los juegos que consumen, además de datos adicionales como si recomiendan o no ese juego, emoticones de gracioso y estadísticas de si el comentario fue útil o no para otros usuarios. También presenta el id del usuario que comenta con su url del perfil y el id del juego que comenta.

* **australian_users_items.json** contiene información sobre los juegos que juegan todos los usuarios, así como el tiempo acumulado que cada usuario jugó a un determinado juego.

* **output_steam_games.json** son datos relacionados con los juegos en sí, como los título, el desarrollador, los precios, entre otros datos.

### Transformaciones

Se ha realizado el proceso ETL (Extracción, Transformación y Carga) de tres conjuntos de datos proporcionados. Se implementaron diversas estrategias para manejar datos anidados, como la transformación de claves de diccionarios en columnas. Se han completado valores faltantes en variables relevantes y eliminado columnas con muchos valores faltantes o que no contribuyen al proyecto, todo esto con el objetivo de optimizar el rendimiento de la API y considerando restricciones de almacenamiento en el despliegue. Se utilizó la biblioteca Pandas para estas transformaciones.

### Feature engineering

Uno de los pedidos para este proyecto fue aplicar un análisis de sentimiento a los reviews de los usuarios. Para ello se creó una nueva columna llamada 'sentiment_analysis' que reemplaza a la columna que contiene los reviews donde clasifica los sentimientos de los comentarios con la siguiente escala:

* 0 si es malo,
* 1 si es neutral o esta sin review
* 2 si es positivo.

Para este proyecto de prueba de concepto, se lleva a cabo un análisis básico de sentimientos utilizando la biblioteca TextBlob en Python, que se basa en procesamiento de lenguaje natural (NLP). El propósito es asignar una polaridad numérica a los comentarios de los usuarios sobre un juego específico, indicando si el sentimiento expresado es negativo, neutral o positivo.

El proceso implica tomar un comentario como entrada, calcular su polaridad de sentimiento con TextBlob y clasificarlo en negativo, neutral o positivo en base a umbrales predefinidos (-0.2 y 0.2) para polaridades. Además, para optimizar la respuesta de las consultas en la API y considerando restricciones de almacenamiento en la nube para el despliegue, se crearon dataframes auxiliares para cada función requerida. Estos dataframes se guardaron en formato parquet, lo que garantiza una eficiente compresión y codificación de los datos.

### Análisis exploratorio de los datos

Se llevó a cabo un Análisis Exploratorio de Datos (EDA) en los tres conjuntos de datos sujetos al proceso ETL, con el fin de identificar las variables adecuadas para la creación del modelo de recomendación. Se utilizó la biblioteca Pandas para la manipulación de los datos, junto con las bibliotecas Matplotlib y Seaborn para la visualización.

Específicamente para el modelo de recomendación, se optó por construir un dataframe personalizado que incluye el ID del usuario que dejó comentarios, los nombres de los juegos sobre los que se comentaron, y una columna de calificación generada a partir de la combinación del análisis de sentimiento y las recomendaciones de juegos.

### Modelo de aprendizaje automático

Generan cada uno, una lista de 5 juegos ya sea ingresando el nombre de un juego o el id de un usuario.
En el primer caso, el modelo tiene una relación ítem-ítem, esto es, se toma un juego y en base a que tan similar es ese juego con el resto de los juegos se recomiendan similares. En el segundo caso, el modelo aplicar un filtro usuario-juego, es decir, toma un usuario, encuentra usuarios similares y se recomiendan ítems que a esos usuarios similares les gustaron.
Para generar estos modelos se adoptaron algoritmos basados en la memoria, los que abordan el problema del filtrado colaborativo utilizando toda la base de datos, tratando de encontrar usuarios similares al usuario activo (es decir, los usuarios para los que se les quiere recomendar) y utilizando sus preferencias para predecir las valoraciones del usuario activo.
Para medir la similitud entre los juegos (item_similarity) y entre los usuarios (user_similarity) se utilizó la similitud del coseno que es una medida comúnmente utilizada para evaluar la similitud entre dos vectores en un espacio multidimensional. En el contexto de sistemas de recomendación y análisis de datos, la similitud del coseno se utiliza para determinar cuán similares son dos conjuntos de datos o elementos, y se calcula utilizando el coseno del ángulo entre los vectores que representan esos datos o elementos.

### Desarrollo de API

* **userdata**: Debe devolver cantidad de dinero gastado por el usuario, el porcentaje de recomendación en base a reviews.recommend y cantidad de items.

* **userforgenre**: Debe devolver el usuario que acumula más horas jugadas para el género dado y una lista de la acumulación de horas jugadas por año de lanzamiento.

* **developer**: Cantidad de items y porcentaje de contenido Free por año según empresa desarrolladora. Ejemplo de retorno.

* **developer_reviews_analysis**: Según el desarrollador, se devuelve un diccionario con el nombre del desarrollador como llave y una lista con la cantidad total de registros de reseñas de usuarios que se encuentren categorizados con un análisis de sentimiento como valor positivo o negativo.

* **recomendacion_juego**:  Ingresando el id de producto, deberíamos recibir una lista con 5 juegos recomendados similares al ingresado.


### Para Visuazlizar mas a fondo el proyecto dejo unos pasos a seguir:

- Clonar el proyecto haciendo `https://github.com/RomeroLautaro/ProyectoSteam`.
- Preparación del entorno de trabajo en Visual Studio Code:
    * Crear entorno `Python -m venv api`
    * Ingresar al entorno haciendo `api\Scripts\activate`
    * Instalar dependencias con `pip install -r requirements.txt`
- Ejecutar el archivo main.py desde consola activando uvicorn. Para ello, hacer `uvicorn main:app --reload`
- Hacer Ctrl + clic sobre la dirección `http://XXX.X.X.X:XXXX` (se muestra en la consola).
- Una vez en el navegador, agregar `/docs` para acceder a ReDoc.
- En cada una de las funciones hacer clic en *Try it out* y luego introducir el dato que requiera o utilizar los ejemplos por defecto. Finalmente Ejecutar y observar la respuesta.