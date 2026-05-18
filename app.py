import streamlit as st
import pandas as pd
import os

# Configuración de la página
st.set_page_config(page_title="Xicopack - Detalle de Producto", page_icon="🌱", layout="centered")

# Estilo personalizado inspirado en tu PDF
st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
    }
    .product-title {
        font-size: 40px;
        font-weight: bold;
        color: #1E4D2B;
        margin-bottom: 0px;
    }
    .sku-label {
        font-size: 24px;
        color: #555;
        margin-bottom: 20px;
    }
    .price-tag {
        font-size: 32px;
        font-weight: bold;
        color: #2E7D32;
        background-color: #E8F5E9;
        padding: 10px;
        border-radius: 10px;
        display: inline-block;
    }
    .footer-text {
        font-style: italic;
        color: #888;
        margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# Cargar datos
@st.cache_data
def load_data():
    path = "productos_catalogo.csv"
    if os.path.exists(path):
        # El CSV ya tiene las columnas SKU, Descripción y Precio
        df = pd.read_csv(path)
        return df
    return None

df = load_data()

# Obtener SKU de la URL
query_params = st.query_params
sku_buscado = query_params.get("sku", "XICO-V12-C") # Default para pruebas

if df is not None:
    # Buscar el producto
    # Intentamos encontrar la columna Clave o SKU
    col_clave = next((c for c in df.columns if 'CLAVE' in c.upper() or 'SKU' in c.upper()), None)
    
    if col_clave:
        # Limpiar el SKU buscado
        sku_buscado = str(sku_buscado).strip()
        
        # Buscar fila exacta
        producto = df[df[col_clave].astype(str).str.strip() == sku_buscado]
        
        if not producto.empty:
            row = producto.iloc[0]
            nombre = row.get('Descripción', 'Producto Xicopack')
            precio = row.get('Precio', 0)
            
            # Mostrar Información
            st.markdown(f"<p class='product-title'>XICOPACK</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='sku-label'>{sku_buscado}</p>", unsafe_allow_html=True)
            
            # Imagen (Busca en carpeta /fotos)
            img_path = f"fotos/{sku_buscado}.jpg"
            if os.path.exists(img_path):
                st.image(img_path, use_column_width=True)
            else:
                st.info("📷 Foto en proceso de carga...")

            st.write(f"**Producto:** {nombre}")
            
            # Selector Caja / Paquete
            es_paquete = sku_buscado.endswith('P')
            modo = st.radio("Seleccionar presentación:", ["Caja", "Paquete"], index=1 if es_paquete else 0)
            
            # Lógica de cambio entre Caja y Paquete
            sku_alternativo = sku_buscado[:-1] if es_paquete else sku_buscado + "P"
            
            if (modo == "Paquete" and not es_paquete) or (modo == "Caja" and es_paquete):
                # Buscar el alternativo
                alt_prod = df[df[col_clave].astype(str).str.strip() == sku_alternativo]
                if not alt_prod.empty:
                    # Redirigir (Simulado actualizando datos)
                    row = alt_prod.iloc[0]
                    sku_buscado = sku_alternativo
                    nombre = row.get('Descripción', nombre)
                    precio = row.get('Precio', precio)
                    st.warning(f"Cambiado a: {sku_buscado}")
            
            st.markdown(f"<div class='price-tag'>${precio:,.2f} MXN</div>", unsafe_allow_html=True)
            
            # Calculadora de Cantidad
            st.divider()
            cantidad = st.number_input("Cantidad a registrar:", min_value=1, value=1)
            total = cantidad * precio
            st.subheader(f"Total: ${total:,.2f}")
            
            if st.button("🛒 Registrar en Inventario (Clip)"):
                st.success(f"Registradas {cantidad} unidades de {sku_buscado}")
                st.balloons()

            st.markdown("<p class='footer-text'>Empaques que vuelven a la tierra</p>", unsafe_allow_html=True)
        else:
            st.error(f"No se encontró el producto con SKU: {sku_buscado}")
    else:
        st.error("No se encontró la columna de 'Clave' en el archivo Excel.")
else:
    st.error("No se pudo cargar el archivo de precios.")
