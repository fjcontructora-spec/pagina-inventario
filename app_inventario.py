import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# 1. CONFIGURACIÓN DE LA PÁGINA (Esto le da el look ancho y el título en la pestaña)
st.set_page_config(
    page_title="Inventario FJ - Gestión Local",
    page_icon="🏗️",
    layout="wide"
)

AZUL_CFJ = "#0169A4"
VERDE_CFJ = "#00B04F"
FONDO_PROFUNDIDAD = "#F4F7F9"
# 2. ESTILO VISUAL (Para que se vea más limpio)
st.markdown(f"""
    <style>
    /* Fondo de la aplicación */
    .stApp {{
        background-color: {FONDO_PROFUNDIDAD};
    }}
    
    /* Estilo de las métricas (Tarjetas blancas con borde verde) */
    div[data-testid="metric-container"] {{
        background-color: #ffffff;
        border-left: 5px solid {VERDE_CFJ}; /* Detalle en verde */
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    
    /* Títulos en Azul */
    h1, h2, h3 {{
        color: {AZUL_CFJ} !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}

    /* Botones y detalles interactivos */
    .stButton>button {{
        background-color: {AZUL_CFJ};
        color: white;
        border-radius: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Asegúrate de que el archivo 'constructora-fj-s-a.png' esté en la misma carpeta que este script
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    st.image("constructora-fj-s-a.png", width=180)

with col_titulo:
    st.title("Sistema de Gestión de Inventario")
    st.write("Panel de Control Operativo - Constructora FJ S.A.")
# 3. FUNCIÓN DE CONEXIÓN (La mantenemos igual pero organizada)
def conectar_db():
    # RECUERDA: Reemplaza 'TU_CLAVE' por la real de Supabase
    usuario = "postgres.ikgqwlnuinegkmlogalv"
    clave = "ll0iJsOa9ZgYStwe" 
    host = "aws-1-sa-east-1.pooler.supabase.com"
    puerto = "6543"
    db = "postgres"
    
    url = f"postgresql://{usuario}:{clave}@{host}:{puerto}/{db}"
    return create_engine(url)

# 4. CARGA DE DATOS
try:
    engine = conectar_db()
    # Traemos los datos de la tabla (o de la vista si la creamos luego)
    df = pd.read_sql("SELECT * FROM fact_fisico", engine)
    
    # --- TÍTULO Y BUSCADOR ---
    st.title("🏗️ Inventario General - Constructora FJ")
    
    # Creamos una fila para el buscador y filtros
    col_busq, col_vacia = st.columns([2, 2])
    with col_busq:
        busqueda = st.text_input("🔍 Buscar material por nombre...", "")

    # Filtrar el dataframe según la búsqueda
    if busqueda:
        df = df[df['recurso_id'].astype(str).str.contains(busqueda, case=False)]

    # 5. PANEL DE MÉTRICAS (Los numeritos de arriba)
    st.subheader("Resumen de Bodega")
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.metric("Ítems Registrados", f"{len(df)}")
    with m2:
        stock_total = df['cantidad'].sum() if 'cantidad' in df else 0
        st.metric("Total Unidades en Stock", f"{stock_total:,.0f}")
    with m3:
        # Aquí podrías poner el valor total si tienes precios
        st.metric("Estado de Conexión", "🟢 En Línea")

    st.divider()

    # 6. TABLA INTERACTIVA
    st.subheader("📋 Detalle de Existencias")
    
    # Configuramos la tabla para que se vea bonita
    st.dataframe(
        df,
        use_container_width=True, # Que ocupe todo el ancho
        hide_index=True,          # Quitar la columna de números de la izquierda
        column_config={
            "cantidad": st.column_config.NumberColumn("Cantidad Actual", format="%d 📦"),
            "fecha": st.column_config.DateColumn("Última Sincronización"),
            "recurso_id": "Identificador de Recurso"
        }
    )

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
