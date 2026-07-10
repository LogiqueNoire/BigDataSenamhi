# Bigdata FAO EcoCrop + LSTM

Este directorio esta organizado para subirlo a GitHub y ejecutar el scraper de FAO EcoCrop con GitHub Actions cada cierto tiempo. Tambien queda preparado para guardar el notebook de Databricks, el modelo LSTM entrenado y los archivos de inferencia que despues puede usar Render.

## Estructura

- `scripts/ecocrop_fao_unificado.py`: descarga datos de FAO EcoCrop, aplica el filtro de especies y completa nombres comunes con GBIF.
- `data/filtro.txt`: lista de especies que se quieren conservar.
- `outputs/`: CSV generados por el script.
- `notebooks/`: notebook de Databricks.
- `models/`: modelo LSTM entrenado y artefactos del modelo.
- `inference/`: codigo y archivos necesarios para inferencia en Render.
- `requirements.txt`: dependencias del scraper.

## Ejecutar localmente

```bash
pip install -r requirements.txt
python scripts/ecocrop_fao_unificado.py
```

Opciones utiles:

```bash
python scripts/ecocrop_fao_unificado.py --sin-filtro
python scripts/ecocrop_fao_unificado.py --sin-nombres-comunes
python scripts/ecocrop_fao_unificado.py --salida outputs/ecocrop_fao_final.csv
```

## GitHub Actions

El workflow esta en `.github/workflows/ecocrop-scheduled.yml`. Ejecuta el script de forma programada y guarda el CSV como artifact de GitHub Actions.

Importante: esta carpeta `bigdata` esta pensada para subirse como raiz del repositorio. Si el repositorio se crea desde una carpeta superior, entonces `.github/workflows` debe estar en la raiz real del repo.

## Databricks y modelo

Coloca el notebook exportado desde Databricks en `notebooks/`.

Coloca el modelo entrenado en `models/`. Si el archivo pesa mas de 100 MB, GitHub no lo acepta como archivo normal; en ese caso usa Git LFS o subelo como release/artifact.

## Render

Los archivos que Render necesite para inferencia deben ir en `inference/`. La idea es que el servicio de Render cargue el modelo desde `models/` y use el codigo de inferencia desde esa carpeta.
