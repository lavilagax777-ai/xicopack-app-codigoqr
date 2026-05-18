import fitz
import pandas as pd
import os
import re

def extraer_fotos_v2(pdf_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    df = pd.read_csv("productos_catalogo.csv")
    skus = df['SKU'].tolist()
    
    doc = fitz.open(pdf_path)
    img_count = 0
    
    print(f"Iniciando extracción profunda en {len(doc)} páginas...")
    
    for page_index in range(len(doc)):
        page = doc[page_index]
        text = page.get_text()
        
        # Encontrar todos los SKUs en esta página usando regex
        page_skus = re.findall(r"Clave:\s*(\S+)", text)
        
        image_list = page.get_images(full=True)
        
        if not image_list:
            continue
            
        # Mapear imágenes por posición (arriba hacia abajo)
        # Obtenemos las coordenadas de las imágenes
        img_info = []
        for img in image_list:
            xref = img[0]
            # Encontrar dónde está la imagen en la página
            rects = page.get_image_rects(xref)
            if rects:
                img_info.append({"xref": xref, "y": rects[0].y0})
        
        # Ordenar imágenes de arriba a abajo
        img_info.sort(key=lambda x: x["y"])
        
        for i, info in enumerate(img_info):
            if i < len(page_skus):
                sku = page_skus[i]
                img_data = doc.extract_image(info["xref"])
                img_bytes = img_data["image"]
                
                with open(os.path.join(output_dir, f"{sku}.jpg"), "wb") as f:
                    f.write(img_bytes)
                img_count += 1

    print(f"¡Éxito! Se recuperaron {img_count} fotos.")

pdf_input = "/Users/luis_genji/Downloads/xicopackPRECIOS.pdf"
extraer_fotos_v2(pdf_input, "fotos")
