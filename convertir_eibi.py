import requests
from datetime import datetime

def descargar_y_convertir_eibi():
    """
    Descarga el archivo CSV de EIBI y lo convierte al formato
    requerido por Skywave Schedules app.
    """
    
    # Lógica CORREGIDA para las temporadas A y B de EIBI
    mes_actual = datetime.now().month
    ano_actual = datetime.now().year % 100  # Últimos 2 dígitos del año
    
    if mes_actual in [11, 12]:  # Noviembre-Diciembre
        temporada = "b"
        ano = ano_actual
    elif mes_actual in [1, 2]:  # Enero-Febrero
        temporada = "b"
        ano = ano_actual - 1  # ¡Usa el archivo B del año anterior!
    else:  # Marzo a Octubre
        temporada = "a"
        ano = ano_actual
        
    nombre_archivo = f"sked-{temporada}{ano:02d}.csv"
    url_eibi = f"http://www.eibispace.de/dx/{nombre_archivo}"
    
    print(f"Descargando {nombre_archivo} desde EIBI...")
    
    try:
        response = requests.get(url_eibi, timeout=30)
        response.raise_for_status()
        
        # EIBI usa Latin-1
        contenido = response.content.decode('latin-1')
        lineas = contenido.splitlines()
        
        if len(lineas) <= 1:
            print("Error: El archivo descargado está vacío o solo tiene cabecera")
            return False
        
        # Guardar con UTF-8
        with open("esch.csv", "w", encoding="utf-8", newline='') as archivo_salida:
            for i, linea in enumerate(lineas):
                # Solo quitar ; del header
                if i == 0:
                    linea = linea.rstrip(';')
                
                archivo_salida.write(linea + "\n")
        
        print(f"✓ Archivo esch.csv creado exitosamente")
        print(f"  Líneas procesadas: {len(lineas)}")
        print(f"  Encoding: UTF-8")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"✗ Error HTTP (archivo {nombre_archivo} no encontrado): {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    exito = descargar_y_convertir_eibi()
    if not exito:
        exit(1)
