import requests
from datetime import datetime, timedelta

def ultimo_domingo(ano, mes):
    """Calcula el último domingo de un mes dado."""
    if mes == 12:
        ultimo_dia = datetime(ano + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = datetime(ano, mes + 1, 1) - timedelta(days=1)
    
    while ultimo_dia.weekday() != 6:
        ultimo_dia -= timedelta(days=1)
    return ultimo_dia

def determinar_temporadas():
    """Devuelve el archivo que corresponde a hoy, y el anterior como respaldo."""
    hoy = datetime.now()
    ano_actual = hoy.year % 100
    
    cambio_marzo = ultimo_domingo(hoy.year, 3)
    cambio_octubre = ultimo_domingo(hoy.year, 10)
    
    if hoy >= cambio_marzo and hoy < cambio_octubre:
        # Temporada A
        actual = f"sked-a{ano_actual:02d}.csv"
        anterior = f"sked-b{ano_actual - 1:02d}.csv"
    elif hoy >= cambio_octubre:
        # Temporada B (fin de año)
        actual = f"sked-b{ano_actual:02d}.csv"
        anterior = f"sked-a{ano_actual:02d}.csv"
    else:
        # Temporada B (principio de año)
        actual = f"sked-b{ano_actual - 1:02d}.csv"
        # El anterior sería el A del año anterior
        anterior = f"sked-a{ano_actual - 1:02d}.csv"
        
    return actual, anterior, hoy, cambio_marzo, cambio_octubre

def descargar_y_convertir_eibi():
    archivo_actual, archivo_anterior, hoy, c_marzo, c_octubre = determinar_temporadas()
    
    print(f"Fechas HFCC para {hoy.year}:")
    print(f"  Cambio a temporada A: {c_marzo.strftime('%Y-%m-%d')}")
    print(f"  Cambio a temporada B: {c_octubre.strftime('%Y-%m-%d')}\n")
    
    # Intentamos descargar el archivo que corresponde por fecha
    exito = intentar_descarga(archivo_actual)
    
    # Si Eibi se retrasó en subir el archivo nuevo (Error 404), intentamos con el anterior
    if not exito:
        print(f"\n⚠️ El archivo {archivo_actual} no existe aún (quizás Eibi se retrasó).")
        print(f"Buscando el archivo de la temporada anterior: {archivo_anterior}...")
        exito = intentar_descarga(archivo_anterior)
        
    return exito

def intentar_descarga(nombre_archivo):
    url_eibi = f"http://www.eibispace.de/dx/{nombre_archivo}"
    print(f"Intentando descargar: {nombre_archivo}")
    
    try:
        response = requests.get(url_eibi, timeout=30)
        response.raise_for_status()
        
        contenido = response.content.decode('latin-1')
        lineas = contenido.splitlines()
        
        if len(lineas) <= 1:
            print("✗ Error: El archivo descargado está vacío o solo tiene cabecera.")
            return False
            
        with open("esch.csv", "w", encoding="utf-8", newline='') as archivo_salida:
            for i, linea in enumerate(lineas):
                if i == 0:
                    linea = linea.rstrip(';')
                archivo_salida.write(linea + "\n")
                
        print(f"✓ ÉXITO: Archivo esch.csv creado desde {nombre_archivo}")
        print(f"  Líneas procesadas: {len(lineas)} | Encoding: UTF-8")
        return True
        
    except requests.exceptions.HTTPError:
        print(f"✗ Error 404: {nombre_archivo} no encontrado en el servidor.")
        return False
    except Exception as e:
        print(f"✗ Error de conexión o sistema: {e}")
        return False

if __name__ == "__main__":
    exito = descargar_y_convertir_eibi()
    if not exito:
        exit(1)
