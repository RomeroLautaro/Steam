from fastapi import FastAPI
import pandas as pd
from fastapi.responses import JSONResponse
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import FastAPI, HTTPException
from typing import List

#Activa siempre el ambiente desde la terminal.
# fastapi-env\Scripts\activate.bat y luego uvicorn main:app --reload
# http://127.0.0.1:8000

app = FastAPI()
@app.get("/developer")
async def developer(desarrollador: str):
    try:
        games = pd.read_parquet('parquet/output_game.parquet')
        
        # Filtrar por empresa desarrolladora
        filtro_dev = games[games['developer'] == desarrollador.capitalize()] 
        
        # Contar la cantidad de juegos por año
        cantidad_x_anio = filtro_dev.groupby('release_year')['id'].size()
        
        # Contar la cantidad de juegos gratuitos por año
        cantidad_gratis = filtro_dev[filtro_dev['price'] == 0].groupby('release_year')['id'].count()
        
        # Calcular el porcentaje de contenido gratuito
        porcentaje_contenido = (cantidad_gratis / cantidad_x_anio * 100).fillna(0).astype(int)
        
        # Crear un DataFrame con los valores
        output = pd.DataFrame({'Año': cantidad_x_anio.index, 'Cantidad': cantidad_x_anio.values, 'Porcentaje Contenido Free': porcentaje_contenido.values})
        
        # Convertir el DataFrame a un diccionario
        output_dict = output.to_dict(orient='records')
        
        # Devolver el diccionario como JSON
        return JSONResponse(content=output_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/userdata")
async def userdata(User_id: str):
    try:
        user = pd.read_parquet('parquet/engineer.parquet')
        
        # Filtrar las revisiones por usuario
        user_reviews = user[user['user_id'] == User_id]
        
        # Obtener la cantidad de dinero gastado por el usuario
        dinero_gastado = user_reviews['price'].sum()
        
        # Calcular el porcentaje de recomendación
        porcentaje_recomendacion = user_reviews['recommend'].mean() * 100
        
        # Obtener la cantidad de items comprados por el usuario
        cantidad_items = user_reviews['item_id'].nunique()
        
        # Crear el diccionario de salida
        output_dict = {
            "Usuario": User_id,
            "Dinero gastado": dinero_gastado,
            "% de recomendación": f"{porcentaje_recomendacion:.2f}%",
            "Cantidad de items": cantidad_items
        }
        
        # Devolver el diccionario como JSON
        return JSONResponse(content=output_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/UserForGenre")
async def UserForGenre(genero: str):
    try:
        ufg = pd.read_parquet('parquet/engineer.parquet')
        
        # Filtrar los datos por el género especificado
        genre_data = ufg[ufg['genres'] == genero]
        
        if genre_data.empty:
            raise HTTPException(status_code=404, detail="No se encontraron datos para el género especificado")
        
        # Encontrar el usuario con más horas jugadas para el género dado
        usuario_mas_horas = genre_data.loc[genre_data['playtime_forever'].idxmax(), 'user_id']
        
        # Calcular la acumulación de horas jugadas por año de lanzamiento
        horas_por_anio = genre_data.groupby('release_year')['playtime_forever'].sum().reset_index()
        horas_por_anio = [{"Año": int(row["release_year"]), "Horas": int(row["playtime_forever"])} for index, row in horas_por_anio.iterrows()]
        
        # Crear el diccionario de salida
        output_dict = {
            "Usuario con más horas jugadas para {}".format(genero): usuario_mas_horas,
            "Horas jugadas": horas_por_anio
        }
        
        # Devolver el diccionario como JSON
        return JSONResponse(content=output_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/developer_reviews_analysis")
async def developer_reviews_analysis(desarrolladora: str):
    try:
        dra = pd.read_parquet('parquet/engineer.parquet')
        
        # Filtrar los datos por el desarrollador especificado
        developer_data = dra[dra['developer'] == desarrolladora]
        
        if developer_data.empty:
            raise HTTPException(status_code=404, detail="No se encontraron datos para el desarrollador especificado")
        
        # Contar los registros de reseñas categorizados como positivos y negativos
        positive_reviews = developer_data[developer_data['sentiment_analysis'] == 'Positive'].shape[0]
        negative_reviews = developer_data[developer_data['sentiment_analysis'] == 'Negative'].shape[0]
        
        # Crear el diccionario de salida
        output_dict = {
            desarrolladora: {"Positive": positive_reviews, "Negative": negative_reviews}
        }
        
        # Devolver el diccionario como JSON
        return JSONResponse(content=output_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Recomendacion por Juego
@app.get("/recomendar/", response_model=List[str])
async def recomendar_juego_api(id_producto: int):
    df_modelo = pd.read_parquet('parquet/modelo.parquet')
    # Obtener recomendaciones para el juego dado
    recomendaciones = recomendacion_juego(id_producto)
    return recomendaciones


# La función recibe un id de un juego y en base a este retorna una lista con juegos similares
def recomendacion_juego(id:int):
    df_modelo = pd.read_parquet('parquet/modelo.parquet')
    # Crea un df con los datos de el id pasado como parametro
    juego = df_modelo[df_modelo['item_id'] == id]
    
    # En caso que el ID no esté en el df, muestra el siguiente mensaje:
    if juego.empty:
        return f"El juego con ID {id} no se encuentra."

    # Obtiene el índice del juego en el DataFrame.
    idx = juego.index[0]

    # Tamaño de la muestra
    muestra = min(2000, len(df_modelo))

    # Ajustamos la semilla aleatoria
    df_sample = df_modelo.sample(n=muestra, random_state=42)
    
    # Calculamos la similitud de contenido solo para el juego dado y la muestra
    sim_scores = cosine_similarity([df_modelo.iloc[idx, 3:]], df_sample.iloc[:, 3:])
    
    # Obtenemos las puntuaciones de similitud del juego dado con otros juegos
    sim_scores = sim_scores[0]

    # Ordenamos los juegos por similitud en orden descendente
    similar_games = [(i, sim_scores[i]) for i in range(len(sim_scores)) if i != idx]
    similar_games = sorted(similar_games, key=lambda x: x[1], reverse=True)

    # Obtenemos los 5 juegos más similares
    similar_game_indices = [i[0] for i in similar_games[:5]]

    # Listamos los juegos similares (solo nombres)
    similar_game_names = df_sample['app_name'].iloc[similar_game_indices].tolist()

    return similar_game_names