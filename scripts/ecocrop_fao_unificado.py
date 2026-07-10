import argparse
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


BASE_URL = "https://ecocrop.apps.fao.org"
SEARCH_URL = BASE_URL + "/ecocrop/srv/en/cropSearch"
DATASHEET_URL = BASE_URL + "/ecocrop/srv/en/dataSheet?id={}"

MATCH_URL = "https://api.gbif.org/v1/species/match"
VERNACULAR_URL = "https://api.gbif.org/v1/species/{}/vernacularNames"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE_URL + "/ecocrop/srv/en/cropSearchForm",
}

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
OUTPUTS_DIR = PROJECT_DIR / "outputs"


def texto(elemento):
    if elemento is None:
        return ""
    return elemento.get_text(" ", strip=True)


def normalizar_nombre(nombre):
    if pd.isna(nombre):
        return ""
    return re.sub(r"\s+", " ", str(nombre).strip()).lower()


def leer_filtro(ruta_filtro):
    ruta = Path(ruta_filtro)
    if not ruta.exists():
        return set()

    nombres = set()
    with ruta.open("r", encoding="utf-8") as archivo:
        for linea in archivo:
            nombre = normalizar_nombre(linea)
            if nombre:
                nombres.add(nombre)
    return nombres


def obtener_ids(cantidad=2568):
    payload = {
        "lifeForm": 0,
        "habit": 0,
        "category": 0,
        "lifeSpan": 0,
        "plantAttribute": 0,
        "opt": 1,
        "minTemperature": "",
        "maxTemperature": "",
        "minRainfall": "",
        "maxRainfall": "",
        "minSoilPh": "",
        "maxSoilPh": "",
        "minLightIntensity": 0,
        "maxLightIntensity": 0,
        "climateZone": 0,
        "photoperiod": 0,
        "latitude": "",
        "altitude": "",
        "availableFieldDays": "",
        "soilDepth": 0,
        "soilTexture": 0,
        "soilFertility": 0,
        "soilSalinity": 0,
        "soilDrainage": 0,
        "mainUse": 0,
        "usedPart": 0,
        "quantity": cantidad,
    }

    session = requests.Session()
    respuesta = session.post(SEARCH_URL, data=payload, headers=HEADERS, timeout=60)
    respuesta.raise_for_status()

    soup = BeautifulSoup(respuesta.text, "html.parser")
    ids = set()

    for enlace in soup.find_all("a", href=True):
        match = re.search(r"id=(\d+)", enlace["href"])
        if match:
            ids.add(int(match.group(1)))

    ids = sorted(ids)
    print(f"Se encontraron {len(ids)} IDs en FAO EcoCrop.")
    return ids


def extraer_datasheet(crop_id):
    try:
        respuesta = requests.get(
            DATASHEET_URL.format(crop_id),
            headers=HEADERS,
            timeout=30,
        )

        if respuesta.status_code != 200:
            return None

        soup = BeautifulSoup(respuesta.text, "html.parser")
        h2 = soup.find("h2")
        if h2 is None:
            return None

        nombre = texto(h2)
        tablas = soup.find_all("table")
        if len(tablas) < 2:
            return None

        filas = tablas[1].find_all("tr")
        if len(filas) <= 4:
            return None

        temperatura = filas[3].find_all(["th", "td"])
        lluvia = filas[4].find_all(["th", "td"])
        if len(temperatura) < 5 or len(lluvia) < 5:
            return None

        print(crop_id, nombre)

        return {
            "ID": crop_id,
            "Scientific Name": nombre,
            "Temperature Opt Min": texto(temperatura[1]),
            "Temperature Opt Max": texto(temperatura[2]),
            "Temperature Abs Min": texto(temperatura[3]),
            "Temperature Abs Max": texto(temperatura[4]),
            "Rainfall Opt Min": texto(lluvia[1]),
            "Rainfall Opt Max": texto(lluvia[2]),
            "Rainfall Abs Min": texto(lluvia[3]),
            "Rainfall Abs Max": texto(lluvia[4]),
        }
    except Exception as error:
        print(f"Error con ID {crop_id}: {error}")
        return None


def descargar_ecocrop(max_workers, cantidad):
    ids = obtener_ids(cantidad=cantidad)
    datos = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(extraer_datasheet, crop_id) for crop_id in ids]

        for future in as_completed(futures):
            resultado = future.result()
            if resultado:
                datos.append(resultado)

    df = pd.DataFrame(datos)
    if not df.empty:
        df.sort_values("ID", inplace=True)
        df.reset_index(drop=True, inplace=True)

    return df


def aplicar_filtro(df, ruta_filtro):
    filtro = leer_filtro(ruta_filtro)
    if not filtro:
        print("No se aplico filtro de cultivos.")
        return df

    antes = len(df)
    df = df[df["Scientific Name"].map(normalizar_nombre).isin(filtro)].copy()
    df.reset_index(drop=True, inplace=True)
    print(f"Filtro aplicado: {len(df)}/{antes} cultivos conservados.")
    return df


def obtener_nombre_comun(nombre_cientifico, session, cache):
    if pd.isna(nombre_cientifico):
        return ""

    nombre_cientifico = str(nombre_cientifico).strip()
    if nombre_cientifico in cache:
        return cache[nombre_cientifico]

    try:
        respuesta = session.get(
            MATCH_URL,
            params={"name": nombre_cientifico},
            timeout=20,
        )

        if respuesta.status_code != 200:
            cache[nombre_cientifico] = ""
            return ""

        usage_key = respuesta.json().get("usageKey")
        if usage_key is None:
            cache[nombre_cientifico] = ""
            return ""

        respuesta = session.get(VERNACULAR_URL.format(usage_key), timeout=20)
        if respuesta.status_code != 200:
            cache[nombre_cientifico] = ""
            return ""

        resultados = respuesta.json().get("results", [])

        for idioma in ("spa", "eng"):
            for item in resultados:
                if item.get("language") == idioma:
                    nombre = item.get("vernacularName", "").strip()
                    cache[nombre_cientifico] = nombre
                    return nombre

        if resultados:
            nombre = resultados[0].get("vernacularName", "").strip()
            cache[nombre_cientifico] = nombre
            return nombre

        cache[nombre_cientifico] = ""
        return ""
    except Exception:
        cache[nombre_cientifico] = ""
        return ""
    finally:
        time.sleep(0.1)


def agregar_nombres_comunes(df):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    cache = {}

    nombres = df["Scientific Name"]
    if tqdm is not None:
        iterable = tqdm(nombres, desc="Buscando nombres comunes")
    else:
        iterable = nombres

    df["Common Name"] = [
        obtener_nombre_comun(nombre, session=session, cache=cache)
        for nombre in iterable
    ]
    return df


def guardar_csv(df, ruta_salida):
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta_salida, index=False, encoding="utf-8-sig")
    print(f"Archivo guardado como: {ruta_salida}")


def main():
    parser = argparse.ArgumentParser(
        description="Descarga datos de FAO EcoCrop, filtra cultivos y agrega nombres comunes con GBIF."
    )
    parser.add_argument("--filtro", default=str(DATA_DIR / "filtro.txt"), help="Archivo TXT con nombres cientificos a conservar.")
    parser.add_argument("--salida", default=str(OUTPUTS_DIR / "ecocrop_fao_final.csv"), help="CSV final de salida.")
    parser.add_argument("--salida-raw", default="", help="Opcional: CSV intermedio sin nombres comunes.")
    parser.add_argument("--workers", type=int, default=20, help="Numero de hilos para descargar datasheets.")
    parser.add_argument("--cantidad", type=int, default=2568, help="Cantidad solicitada al buscador de FAO EcoCrop.")
    parser.add_argument("--sin-filtro", action="store_true", help="No usar filtro.txt aunque exista.")
    parser.add_argument("--sin-nombres-comunes", action="store_true", help="No consultar GBIF.")
    args = parser.parse_args()

    df = descargar_ecocrop(max_workers=args.workers, cantidad=args.cantidad)
    if df.empty:
        print("No se descargaron registros validos.")
        return

    if not args.sin_filtro:
        df = aplicar_filtro(df, args.filtro)

    if args.salida_raw:
        guardar_csv(df, args.salida_raw)

    if not args.sin_nombres_comunes:
        df = agregar_nombres_comunes(df)
        encontrados = (df["Common Name"] != "").sum()
        print(f"Nombres comunes encontrados: {encontrados}/{len(df)}")

    guardar_csv(df, args.salida)
    print("Proceso terminado.")
    print(f"Total de cultivos: {len(df)}")


if __name__ == "__main__":
    main()
