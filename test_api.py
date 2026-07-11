"""
Script de prueba para la API de Predicción Climática
Prueba todos los endpoints con estaciones reales
"""

import requests
import json
from datetime import datetime

# URL base de la API (cambiar según despliegue)
BASE_URL = "http://localhost:8000"

def print_separator(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def test_root():
    """Prueba endpoint raíz"""
    print_separator("TEST 1: Endpoint Raíz (GET /)")
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    return response.status_code == 200

def test_estaciones():
    """Prueba listado de estaciones"""
    print_separator("TEST 2: Listado de Estaciones (GET /estaciones)")
    
    response = requests.get(f"{BASE_URL}/estaciones")
    print(f"Status: {response.status_code}")
    
    data = response.json()
    print(f"\nTotal estaciones: {data['total_estaciones']}")
    print(f"Modelos cargados: {data['modelos_cargados']}")
    print(f"\nEstaciones disponibles:")
    
    for est in data['estaciones']:
        status = "✅" if est['modelo_disponible'] else "❌"
        print(f"  {status} {est['id']:<12} | {est['nombre']:<30} | {est['provincia']}")
    
    return response.status_code == 200

def test_estacion_individual(estacion_id="108068"):
    """Prueba información de una estación específica"""
    print_separator(f"TEST 3: Información Estación (GET /estacion/{estacion_id})")
    
    response = requests.get(f"{BASE_URL}/estacion/{estacion_id}")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    return response.status_code == 200

def test_prediccion(estacion_id="108068", dias=7):
    """Prueba predicción climática"""
    print_separator(f"TEST 4: Predicción Climática (POST /predecir)")
    
    payload = {
        "estacion_id": estacion_id,
        "dias": dias
    }
    
    print(f"Request payload:")
    print(json.dumps(payload, indent=2))
    print(f"\nEnviando solicitud...")
    
    response = requests.post(
        f"{BASE_URL}/predecir",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nEstación: {data['estacion_nombre']} ({data['provincia']})")
        print(f"Días predichos: {data['dias_predichos']}")
        print(f"Fecha generación: {data['fecha_generacion']}")
        
        print(f"\n📊 PROMEDIOS:")
        promedios = data['promedios']
        print(f"  🌡️  Temp. Máxima: {promedios['temperatura_max_promedio']}°C")
        print(f"  🌡️  Temp. Mínima: {promedios['temperatura_min_promedio']}°C")
        print(f"  🌧️  Precipitación: {promedios['precipitacion_acumulada']} mm")
        print(f"  💧 Humedad: {promedios['humedad_promedio']}%")
        
        print(f"\n📅 PRIMEROS 3 DÍAS:")
        for pred in data['predicciones'][:3]:
            print(f"  {pred['fecha']} | "
                  f"Tmax: {pred['temperatura_max']:5.1f}°C | "
                  f"Tmin: {pred['temperatura_min']:5.1f}°C | "
                  f"Precip: {pred['precipitacion']:6.1f}mm | "
                  f"Hum: {pred['humedad']:4.1f}%")
    else:
        print(f"Error: {response.json()}")
    
    return response.status_code == 200

def test_health():
    """Prueba health check"""
    print_separator("TEST 5: Health Check (GET /health)")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    return response.status_code == 200

def test_error_estacion_inexistente():
    """Prueba error con estación inexistente"""
    print_separator("TEST 6: Error - Estación Inexistente")
    
    payload = {
        "estacion_id": "XXXXXX",
        "dias": 7
    }
    
    response = requests.post(f"{BASE_URL}/predecir", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Respuesta: {response.json()}")
    
    return response.status_code == 404

def test_error_dias_invalidos():
    """Prueba error con días inválidos"""
    print_separator("TEST 7: Error - Días Inválidos")
    
    payload = {
        "estacion_id": "108068",
        "dias": 50  # Fuera de rango (1-30)
    }
    
    response = requests.post(f"{BASE_URL}/predecir", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Respuesta: {response.json()}")
    
    return response.status_code == 400

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "🧪"*35)
    print(" "*20 + "INICIANDO PRUEBAS DE API")
    print("🧪"*35)
    print(f"\nURL Base: {BASE_URL}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Endpoint raíz", test_root),
        ("Listado de estaciones", test_estaciones),
        ("Información de estación", test_estacion_individual),
        ("Predicción climática", test_prediccion),
        ("Health check", test_health),
        ("Error estación inexistente", test_error_estacion_inexistente),
        ("Error días inválidos", test_error_dias_invalidos)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"\n❌ Error ejecutando {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen final
    print_separator("RESUMEN DE PRUEBAS")
    
    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{status} | {nombre}")
    
    print(f"\n{'='*70}")
    print(f"RESULTADO FINAL: {exitosos}/{total} pruebas exitosas")
    print(f"{'='*70}\n")
    
    return exitosos == total

if __name__ == "__main__":
    try:
        exito = run_all_tests()
        exit(0 if exito else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar a la API")
        print(f"   Verifica que la API esté corriendo en {BASE_URL}")
        print("   Ejecuta: uvicorn app:app --reload")
        exit(1)
