#!/opt/anaconda3/bin/python
import pandas as pd
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import os
import tempfile

import traceback

def generar_codigos_qr(archivo_entrada, archivo_salida_pdf):
    """
    Lee un archivo Excel o CSV con productos (solo necesita la columna SKU),
    genera un código QR para cada uno, y los organiza en un PDF listo para imprimir.
    """
    print(f"Leyendo archivo: {archivo_entrada}")
    
    # Detectar el tipo de archivo y leer los datos
    _, ext = os.path.splitext(archivo_entrada)
    try:
        if ext.lower() == '.csv':
            df = pd.read_csv(archivo_entrada)
        elif ext.lower() in ['.xls', '.xlsx']:
            # Intentar leer primero normal
            df = pd.read_excel(archivo_entrada)
            
            # Si las columnas parecen no tener SKU/Clave, intentar con la segunda fila como encabezado
            def tiene_sku(columns):
                return any(k in str(c).upper() for c in columns for k in ['SKU', 'CLAVE', 'CODIGO'])
            
            if not tiene_sku(df.columns):
                df_header2 = pd.read_excel(archivo_entrada, header=1)
                if tiene_sku(df_header2.columns):
                    df = df_header2
        else:
            raise ValueError(f"Formato no soportado: {ext}")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    # Validar que exista la columna SKU
    col_sku = None
    for c in df.columns:
        c_upper = str(c).upper().strip()
        if any(k in c_upper for k in ['SKU', 'CLAVE', 'CODIGO', 'REFERENCIA']):
            col_sku = c
            break
            
    if not col_sku:
        print(f"Error: No se encontró columna de identificación (SKU/Clave).")
        print(f"Columnas detectadas: {list(df.columns)}")
        return

    print(f"Columna detectada: '{col_sku}'")

    # Configuración del PDF (tamaño carta: 8.5 x 11 pulgadas)
    try:
        c = canvas.Canvas(archivo_salida_pdf, pagesize=letter)
        ancho_pagina, alto_pagina = letter
        
        # Configuración de la cuadrícula para etiquetas
        columnas = 3
        filas = 5 
        margen_x = 0.5 * inch
        margen_y = 0.5 * inch
        
        espacio_x = (ancho_pagina - 2 * margen_x) / columnas
        espacio_y = (alto_pagina - 2 * margen_y) / filas
        
        # Tamaño del QR en el PDF
        qr_size = 1.5 * inch
        
        col_actual = 0
        fila_actual = 0
        
        total_productos = len(df)
        procesados = 0

        # URL Base de tu aplicación en Streamlit Cloud
        # Si le pusiste otro nombre al repositorio, cámbialo aquí:
        URL_BASE = "https://xicopack-app.streamlit.app"

        # Usamos un directorio temporal para guardar las imágenes de los QR
        with tempfile.TemporaryDirectory() as temp_dir:
            for index, row in df.iterrows():
                sku_raw = row[col_sku]
                if pd.isna(sku_raw):
                    continue
                    
                sku = str(sku_raw).strip()
                if sku == '' or sku.lower() == 'nan':
                    continue
                
                # Crear el enlace dinámico
                enlace_qr = f"{URL_BASE}?sku={sku}"
                    
                # Generar imagen QR
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(enlace_qr) # Ahora guarda el link, no solo el texto
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Nombre seguro para archivo temporal
                safe_sku = "".join([char for char in sku if char.isalnum() or char in ('-','_')]).rstrip()
                if not safe_sku:
                    safe_sku = f"item_{index}"
                    
                img_path = os.path.join(temp_dir, f"{safe_sku}.png")
                img.save(img_path)
                
                # Calcular posición
                pos_x = margen_x + col_actual * espacio_x
                pos_y = alto_pagina - margen_y - (fila_actual + 1) * espacio_y
                
                # Dibujar
                offset_x = (espacio_x - qr_size) / 2
                c.drawImage(img_path, pos_x + offset_x, pos_y + 0.4 * inch, width=qr_size, height=qr_size)
                
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(pos_x + espacio_x / 2, pos_y + 0.2 * inch, f"SKU: {sku}")
                
                col_actual += 1
                if col_actual >= columnas:
                    col_actual = 0
                    fila_actual += 1
                    if fila_actual >= filas:
                        c.showPage()
                        col_actual = 0
                        fila_actual = 0
                
                procesados += 1

        c.save()
        print(f"\n¡Éxito! PDF generado en: {archivo_salida_pdf}")
        print(f"Total de etiquetas generadas: {procesados} (de {total_productos} filas)")
    except Exception as e:
        print(f"Error durante la generación del PDF: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    # Prioridades de archivos a buscar
    POSIBLES_ARCHIVOS = [
        "productos_catalogo.csv",
        "/Users/luis_genji/Downloads/ListaPreciosultima.xlsx",
        "productos.csv"
    ]
    
    archivo_a_usar = None
    for ruta in POSIBLES_ARCHIVOS:
        if os.path.exists(ruta):
            archivo_a_usar = ruta
            break
            
    if not archivo_a_usar:
        print("Error: No se encontró ningún archivo de datos.")
        print(f"Buscamos en: {POSIBLES_ARCHIVOS}")
        exit(1)

    print(f"--- Iniciando sistema de generación QR Xicopack ---")
    print(f"Usando datos de: {archivo_a_usar}")
    generar_codigos_qr(archivo_a_usar, "etiquetas_xicopack.pdf")

