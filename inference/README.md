# Inferencia

Aqui van los archivos que usara Render para servir predicciones con el modelo LSTM.

Estructura sugerida:

- `app.py`: API o servicio web para Render.
- `predict.py`: funciones de carga del modelo y prediccion.
- `schemas.py`: validacion de entradas, si usas FastAPI o Pydantic.
- `requirements.txt`: dependencias especificas de inferencia, si son distintas a las del scraper.

La inferencia deberia cargar el modelo desde `../models/` y recibir datos nuevos para producir predicciones.
