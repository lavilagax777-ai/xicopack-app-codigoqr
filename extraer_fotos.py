import fitz # PyMuPDF
import pandas as pd
import os

def extraer_fotos_pdf(pdf_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Cargar el CSV que generamos para saber qué SKUs buscar
    df = pd.read_csv("productos_catalogo.csv")
    skus = df['SKU'].tolist()
    
    doc = fitz.open(pdf_path)
    img_count = 0
    sku_idx = 0
    
    print(f"Buscando imágenes en {len(doc)} páginas...")
    
    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)
        
        # En este PDF, cada página suele tener 6 productos y 6 imágenes.
        # Las imágenes suelen venir en el orden de los productos.
        
        # Obtenemos los SKUs que aparecen en esta página
        text = page.get_text()
        page_skus = []
        for sku in skus:
            if f"Clave: {sku}" in text:
                page_skus.append(sku)
        
        for img_idx, img in enumerate(image_list):
            if sku_idx >= len(skus): break
            
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Intentamos mapear la imagen al SKU de la página
            if img_idx < len(page_skus):
                sku = page_skus[img_idx]
                img_name = f"{sku}.jpg"
                with open(os.path.join(output_dir, img_name), "wb") as f:
                    f.write(image_bytes)
                img_count += 1

    print(f"Proceso terminado. Se guardaron {img_count} imágenes en {output_dir}")

pdf_input = "/Users/luis_genji/Downloads/xicopackPRECIOS.pdf"
extraer_fotos_pdf(pdf_input, "fotos")
