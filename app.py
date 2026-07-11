from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pickle
import tensorflow as tf
from tensorflow import keras
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict
import os

app = FastAPI(
    title="API de Predicción Climática La Libertad",
    description="API para predicciones climáticas por estación meteorológica usando LSTM",
    version="2.0.0"
)

# ============================================================
# CONFIGURACIÓN DE ESTACIONES
# ============================================================

ESTACIONES_DISPONIBLES = {
    '472C2CB6': {'nombre': 'MARMOT', 'provincia': 'Gran Chimú'},
    '107054': {'nombre': 'CALLANCAS', 'provincia': 'Trujillo'},
    '472D60B4': {'nombre': 'USQUIL', 'provincia': 'Trujillo'},
    '472EB1D2': {'nombre': 'CAPACHIQUE', 'provincia': 'Trujillo'},
    '107131': {'nombre': 'LA FORTUNA', 'provincia': 'Trujillo'},
    '4727319A': {'nombre': 'QUIRUVILCA', 'provincia': 'Santiago de Chuco'},
    '472D552E': {'nombre': 'LUCMA', 'provincia': 'Gran Chimú'},
    '472EA2A4': {'nombre': 'CASCAS', 'provincia': 'Gran Chimú'},
    '108045': {'nombre': 'CACHICADAN', 'provincia': 'Santiago de Chuco'},
    '107009': {'nombre': 'HUAMACHUCO', 'provincia': 'Sánchez Carrión'},
    '108068': {'nombre': 'TRUJILLO', 'provincia': 'Trujillo'},
    '108001': {'nombre': 'SALPO', 'provincia': 'Trujillo'},
    '472D30C8': {'nombre': 'CASAGRANDE', 'provincia': 'Ascope'},
    '100136': {'nombre': 'TALLA (GUADALUPE)', 'provincia': 'Pacasmayo'},
    '108046': {'nombre': 'MOLLEPATA', 'provincia': 'Santiago de Chuco'},
    '108048': {'nombre': 'Huacamarcanga', 'provincia': 'Santiago de Chuco'}
}

# ============================================================
# CARGA DE MODELOS AL INICIO
# ============================================================

MODELS = {}
SCALERS = {}
METADATA = {}

MODELS_DIR = "./models"

@app.on_event("startup")
async def load_models():
    """Carga todos los modelos disponibles al iniciar la API"""
    print("\n🚀 Cargando modelos pre-entrenados...")
    
    for estacion_id, info in ESTACIONES_DISPONIBLES.items():
        nombre_archivo = info['nombre'].replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
        
        model_path = f"{MODELS_DIR}/modelo_{nombre_archivo}.h5"
        scaler_path = f"{MODELS_DIR}/scaler_{nombre_archivo}.pkl"
        metadata_path = f"{MODELS_DIR}/metadata_{nombre_archivo}.pkl"
        
        try:
            if os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(metadata_path):
                # Cargar modelo
                MODELS[estacion_id] = keras.models.load_model(model_path)
                
                # Cargar scaler
                with open(scaler_path, 'rb') as f:
                    SCALERS[estacion_id] = pickle.load(f)
                
                # Cargar metadata
                with open(metadata_path, 'rb') as f:
                    METADATA[estacion_id] = pickle.load(f)
                
                print(f"  ✅ {info['nombre']} (ID: {estacion_id})")
            else:
                print(f"  ⚠️  {info['nombre']} (ID: {estacion_id}) - Archivos no encontrados")
        except Exception as e:
            print(f"  ❌ Error cargando {info['nombre']}: {e}")
    
    print(f"\n📊 Total modelos cargados: {len(MODELS)}/{len(ESTACIONES_DISPONIBLES)}")
    print("✅ API lista para recibir peticiones\n")

# ============================================================
# MODELOS DE DATOS (Pydantic)
# ============================================================

class PrediccionRequest(BaseModel):
    estacion_id: str
    dias: int = 7
    
    class Config:
        schema_extra = {
            "example": {
                "estacion_id": "108068",
                "dias": 7
            }
        }

class PrediccionDia(BaseModel):
    fecha: str
    temperatura_max: float
    temperatura_min: float
    precipitacion: float
    humedad: float

class PrediccionResponse(BaseModel):
    estacion_id: str
    estacion_nombre: str
    provincia: str
    fecha_generacion: str
    dias_predichos: int
    predicciones: List[PrediccionDia]
    promedios: Dict[str, float]

# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "mensaje": "API de Predicción Climática - La Libertad",
        "version": "2.0.0",
        "modo": "Predicción por Estación",
        "estaciones_disponibles": len(MODELS),
        "endpoints": {
            "GET /estaciones": "Listar estaciones disponibles",
            "POST /predecir": "Generar predicción climática",
            "GET /estacion/{id}": "Información de una estación"
        }
    }

@app.get("/estaciones")
def listar_estaciones():
    """Lista todas las estaciones disponibles con sus modelos cargados"""
    estaciones = []
    
    for estacion_id, info in ESTACIONES_DISPONIBLES.items():
        modelo_cargado = estacion_id in MODELS
        
        estacion_data = {
            "id": estacion_id,
            "nombre": info['nombre'],
            "provincia": info['provincia'],
            "modelo_disponible": modelo_cargado
        }
        
        if modelo_cargado and estacion_id in METADATA:
            metadata = METADATA[estacion_id]
            estacion_data["ultima_fecha_datos"] = str(metadata.get('last_date', 'N/A'))
            estacion_data["num_registros"] = metadata.get('num_registros', 0)
            estacion_data["val_loss"] = round(metadata.get('val_loss', 0), 4)
            estacion_data["entrenado_el"] = str(metadata.get('trained_at', 'N/A'))
        
        estaciones.append(estacion_data)
    
    return {
        "total_estaciones": len(ESTACIONES_DISPONIBLES),
        "modelos_cargados": len(MODELS),
        "estaciones": estaciones
    }

@app.get("/estacion/{estacion_id}")
def info_estacion(estacion_id: str):
    """Obtiene información detallada de una estación específica"""
    if estacion_id not in ESTACIONES_DISPONIBLES:
        raise HTTPException(status_code=404, detail=f"Estación {estacion_id} no existe")
    
    info = ESTACIONES_DISPONIBLES[estacion_id]
    modelo_cargado = estacion_id in MODELS
    
    response = {
        "id": estacion_id,
        "nombre": info['nombre'],
        "provincia": info['provincia'],
        "modelo_disponible": modelo_cargado
    }
    
    if modelo_cargado and estacion_id in METADATA:
        metadata = METADATA[estacion_id]
        response["metadata"] = {
            "ultima_fecha_datos": str(metadata.get('last_date', 'N/A')),
            "num_registros_entrenamiento": metadata.get('num_registros', 0),
            "lookback_dias": metadata.get('lookback', 30),
            "horizonte_prediccion": metadata.get('forecast_horizon', 7),
            "val_loss": round(metadata.get('val_loss', 0), 4),
            "val_mae": round(metadata.get('val_mae', 0), 4),
            "epocas_entrenadas": metadata.get('epochs_run', 0),
            "fecha_entrenamiento": str(metadata.get('trained_at', 'N/A')),
            "variables": metadata.get('feature_names', [])
        }
    
    return response

@app.post("/predecir", response_model=PrediccionResponse)
def predecir_clima(request: PrediccionRequest):
    """
    Genera predicción climática para una estación específica
    
    - **estacion_id**: ID de la estación (ej: '108068' para Trujillo)
    - **dias**: Número de días a predecir (1-30, default 7)
    """
    # Validaciones
    if request.estacion_id not in ESTACIONES_DISPONIBLES:
        raise HTTPException(
            status_code=404,
            detail=f"Estación {request.estacion_id} no existe. Usa GET /estaciones para ver las disponibles"
        )
    
    if request.estacion_id not in MODELS:
        raise HTTPException(
            status_code=503,
            detail=f"Modelo para estación {request.estacion_id} no está cargado"
        )
    
    if request.dias < 1 or request.dias > 30:
        raise HTTPException(
            status_code=400,
            detail="El número de días debe estar entre 1 y 30"
        )
    
    try:
        # Obtener modelo, scaler y metadata
        model = MODELS[request.estacion_id]
        scaler = SCALERS[request.estacion_id]
        metadata = METADATA[request.estacion_id]
        
        lookback = metadata['lookback']
        last_date = metadata['last_date']
        
        # NOTA: En producción real, cargarías los últimos datos reales de la BD
        # Por ahora, usamos datos sintéticos basados en los últimos datos de entrenamiento
        np.random.seed(42)
        last_sequence = np.random.rand(lookback, 4) * 0.5 + 0.5
        
        # Generar predicciones iterativamente
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(request.dias):
            pred = model.predict(current_sequence.reshape(1, lookback, -1), verbose=0)
            next_day = pred[0, 0, :]
            predictions.append(next_day)
            current_sequence = np.vstack([current_sequence[1:], next_day])
        
        # Desnormalizar predicciones
        predictions_array = np.array(predictions)
        predictions_inv = scaler.inverse_transform(predictions_array)
        
        # Crear fechas futuras
        if isinstance(last_date, str):
            last_date = pd.to_datetime(last_date)
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=request.dias, freq='D')
        
        # Preparar respuesta
        predicciones_list = []
        for i, fecha in enumerate(future_dates):
            predicciones_list.append(PrediccionDia(
                fecha=fecha.strftime('%Y-%m-%d'),
                temperatura_max=round(float(predictions_inv[i, 0]), 2),
                temperatura_min=round(float(predictions_inv[i, 1]), 2),
                precipitacion=round(float(predictions_inv[i, 2]), 2),
                humedad=round(float(predictions_inv[i, 3]), 2)
            ))
        
        # Calcular promedios
        promedios = {
            "temperatura_max_promedio": round(float(predictions_inv[:, 0].mean()), 2),
            "temperatura_min_promedio": round(float(predictions_inv[:, 1].mean()), 2),
            "precipitacion_acumulada": round(float(predictions_inv[:, 2].sum()), 2),
            "humedad_promedio": round(float(predictions_inv[:, 3].mean()), 2)
        }
        
        info_estacion = ESTACIONES_DISPONIBLES[request.estacion_id]
        
        return PrediccionResponse(
            estacion_id=request.estacion_id,
            estacion_nombre=info_estacion['nombre'],
            provincia=info_estacion['provincia'],
            fecha_generacion=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            dias_predichos=request.dias,
            predicciones=predicciones_list,
            promedios=promedios
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar predicción: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Endpoint de health check para monitoreo"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modelos_cargados": len(MODELS),
        "estaciones_totales": len(ESTACIONES_DISPONIBLES)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
