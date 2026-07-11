# 🌤️ API de Predicción Climática - La Libertad, Perú

API REST para predicciones climáticas por estación meteorológica usando modelos LSTM pre-entrenados. Sistema optimizado que predice temperatura, precipitación y humedad para las **16 estaciones** de La Libertad.

---

## 🎯 Características

- ⚡ **Ultra-rápido**: Predicciones en **1-2 segundos** (modelos pre-cargados en memoria)
- 📡 **16 Estaciones**: Cobertura completa de La Libertad
- 🧠 **Modelos LSTM**: Entrenados con datos históricos reales (hasta 43,000+ registros por estación)
- 🔄 **Sin re-entrenamiento**: API lista para producción
- 📊 **FastAPI**: Documentación interactiva automática

---

## 📡 Estaciones Disponibles

| ID | Nombre | Provincia | Registros |
|----|--------|-----------|-----------|
| **472C2CB6** | MARMOT | Gran Chimú | 43,677 |
| **107054** | CALLANCAS | Trujillo | 43,504 |
| **472D60B4** | USQUIL | Trujillo | 43,084 |
| **472EB1D2** | CAPACHIQUE | Trujillo | 42,754 |
| **107131** | LA FORTUNA | Trujillo | 42,334 |
| **4727319A** | QUIRUVILCA | Santiago de Chuco | 41,438 |
| **472D552E** | LUCMA | Gran Chimú | 41,345 |
| **472EA2A4** | CASCAS | Gran Chimú | 40,248 |
| **108045** | CACHICADAN | Santiago de Chuco | 3,384 |
| **107009** | HUAMACHUCO | Sánchez Carrión | 3,368 |
| **108068** | TRUJILLO | Trujillo | 3,164 |
| **108001** | SALPO | Trujillo | 3,134 |
| **472D30C8** | CASAGRANDE | Ascope | 2,766 |
| **100136** | TALLA (GUADALUPE) | Pacasmayo | 1,826 |
| **108046** | MOLLEPATA | Santiago de Chuco | 1,826 |
| **108048** | Huacamarcanga | Santiago de Chuco | 1,826 |

---

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/clima-api.git
cd clima-api

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Ejecutar API

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

La API estará disponible en: **http://localhost:8000**

### 3. Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📚 Endpoints

### 1. **Información General**
```http
GET /
```

**Respuesta:**
```json
{
  "mensaje": "API de Predicción Climática - La Libertad",
  "version": "2.0.0",
  "modo": "Predicción por Estación",
  "estaciones_disponibles": 16
}
```

---

### 2. **Listar Estaciones**
```http
GET /estaciones
```

**Respuesta:**
```json
{
  "total_estaciones": 16,
  "modelos_cargados": 16,
  "estaciones": [
    {
      "id": "108068",
      "nombre": "TRUJILLO",
      "provincia": "Trujillo",
      "modelo_disponible": true,
      "ultima_fecha_datos": "2026-05-19",
      "num_registros": 3164,
      "val_loss": 0.0021
    }
  ]
}
```

---

### 3. **Información de Estación**
```http
GET /estacion/{estacion_id}
```

**Ejemplo:**
```bash
curl http://localhost:8000/estacion/108068
```

**Respuesta:**
```json
{
  "id": "108068",
  "nombre": "TRUJILLO",
  "provincia": "Trujillo",
  "modelo_disponible": true,
  "metadata": {
    "ultima_fecha_datos": "2026-05-19",
    "num_registros_entrenamiento": 3164,
    "lookback_dias": 30,
    "horizonte_prediccion": 7,
    "val_loss": 0.0021,
    "val_mae": 0.032,
    "epocas_entrenadas": 15,
    "variables": ["TemperaturaMax", "TemperaturaMin", "Precipitacion", "Humedad"]
  }
}
```

---

### 4. **Generar Predicción** ⭐
```http
POST /predecir
Content-Type: application/json
```

**Body:**
```json
{
  "estacion_id": "108068",
  "dias": 7
}
```

**Respuesta:**
```json
{
  "estacion_id": "108068",
  "estacion_nombre": "TRUJILLO",
  "provincia": "Trujillo",
  "fecha_generacion": "2026-07-10 18:30:00",
  "dias_predichos": 7,
  "promedios": {
    "temperatura_max_promedio": 25.2,
    "temperatura_min_promedio": 17.8,
    "precipitacion_acumulada": 12.5,
    "humedad_promedio": 82.3
  },
  "predicciones": [
    {
      "fecha": "2026-05-20",
      "temperatura_max": 26.1,
      "temperatura_min": 18.2,
      "precipitacion": 1.8,
      "humedad": 83.5
    }
  ]
}
```

**Ejemplo con cURL:**
```bash
curl -X POST http://localhost:8000/predecir \
  -H "Content-Type: application/json" \
  -d '{"estacion_id": "108068", "dias": 7}'
```

**Ejemplo con Python:**
```python
import requests

response = requests.post(
    'http://localhost:8000/predecir',
    json={'estacion_id': '108068', 'dias': 7}
)

data = response.json()
print(f"Predicción para {data['estacion_nombre']}")
print(f"Temp. promedio: {data['promedios']['temperatura_max_promedio']}°C")
```

---

### 5. **Health Check**
```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2026-07-10T18:30:00",
  "modelos_cargados": 16,
  "estaciones_totales": 16
}
```

---

## 🧪 Pruebas

Ejecutar suite de pruebas completa:

```bash
python test_api.py
```

**Salida esperada:**
```
✅ PASS | Endpoint raíz
✅ PASS | Listado de estaciones
✅ PASS | Información de estación
✅ PASS | Predicción climática
✅ PASS | Health check
✅ PASS | Error estación inexistente
✅ PASS | Error días inválidos

RESULTADO FINAL: 7/7 pruebas exitosas
```

---

## 📦 Estructura del Proyecto

```
clima-api/
├── app.py                      # API FastAPI
├── test_api.py                 # Script de pruebas
├── requirements.txt            # Dependencias
├── README.md                   # Esta documentación
└── models/                     # Modelos pre-entrenados (48 archivos)
    ├── modelo_TRUJILLO.h5
    ├── scaler_TRUJILLO.pkl
    ├── metadata_TRUJILLO.pkl
    ├── modelo_MARMOT.h5
    ├── scaler_MARMOT.pkl
    ├── metadata_MARMOT.pkl
    └── ... (3 archivos × 16 estaciones = 48)
```

---

## 🛠️ Tecnologías

- **FastAPI** 0.104+ - Framework web moderno
- **TensorFlow** 2.21+ - Modelos LSTM
- **scikit-learn** 1.5+ - Normalización de datos
- **pandas** 2.2+ - Manipulación de datos
- **numpy** 2.0+ - Cálculos numéricos
- **uvicorn** - Servidor ASGI

---

## 🌐 Despliegue en Render

### 1. Preparar repositorio

```bash
# Asegurar que tienes la carpeta models/ con los 48 archivos
ls models/ | wc -l  # Debe mostrar 48

# Commit y push
git add .
git commit -m "Agregar modelos LSTM pre-entrenados por estación"
git push
```

### 2. Configurar en Render

1. Crear nuevo **Web Service**
2. Conectar repositorio GitHub
3. Configurar:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11+

### 3. Variables de Entorno (opcional)

No se requieren variables de entorno para la versión actual. Los modelos se cargan desde `./models/`.

---

## 📊 Rendimiento

| Métrica | Valor |
|---------|-------|
| Tiempo de carga inicial | ~5-10s (16 modelos) |
| Tiempo de predicción | 1-2s |
| Memoria RAM | ~800MB-1GB |
| Tamaño modelos | ~15MB total |

---

## 🔮 Roadmap

- [ ] Conexión a base de datos en vivo para datos reales
- [ ] Caché de predicciones
- [ ] Gráficos interactivos
- [ ] Alertas climáticas
- [ ] API de recomendación de cultivos por estación
- [ ] Integración con frontend React/Vue

---

## 📝 Notas Técnicas

### Modelos LSTM

- **Arquitectura**: LSTM(32) → Dropout(0.2) → Dense → Reshape
- **Lookback**: 30 días históricos
- **Horizonte**: 7 días de predicción nativa
- **Variables**: Temperatura máx/mín, precipitación, humedad
- **Normalización**: MinMaxScaler (0, 1)

### Datos de Entrenamiento

- **Fuente**: Estaciones meteorológicas SENAMHI
- **Período**: Datos históricos completos por estación (variable según estación)
- **Frecuencia**: Diaria
- **Split**: Train 85% / Val 15%

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crear branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

---

## 📄 Licencia

MIT License - ver archivo LICENSE

---

## 👨‍💻 Autor

**Tu Nombre**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- Email: tu-email@example.com

---

## 🙏 Agradecimientos

- **SENAMHI** - Datos meteorológicos
- **Databricks** - Plataforma de desarrollo
- **Universidad** - Apoyo académico

---

**¿Problemas o sugerencias?** Abre un [issue](https://github.com/tu-usuario/clima-api/issues) 🚀
