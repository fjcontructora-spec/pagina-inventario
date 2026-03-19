import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# 1. CONFIGURACIÓN DE LA PÁGINA (Esto le da el look ancho y el título en la pestaña)
st.set_page_config(
    page_title="Inventario FJ - Gestión Local",
    page_icon="constructora-fj-s-a.png",
    layout="wide"
)

def check_password():
    """Devuelve True si el usuario ingresó la contraseña correcta."""

    def password_entered():
        """Verifica si la contraseña ingresada coincide."""
        if st.session_state["username"] == st.secrets["admin_user"] and \
           st.session_state["password"] == st.secrets["admin_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # No guardar la contraseña en sesión
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Primera vez, mostrar el formulario
        st.title("🔒 Acceso Restringido - Constructora FJ")
        st.text_input("Usuario", on_change=password_entered, key="username")
        st.text_input("Contraseña", type="password", on_change=password_entered, key="password")
        return False
    
    elif not st.session_state["password_correct"]:
        # Contraseña incorrecta, volver a mostrar el formulario con error
        st.error("😕 Usuario o contraseña incorrectos")
        st.text_input("Usuario", on_change=password_entered, key="username")
        st.text_input("Contraseña", type="password", on_change=password_entered, key="password")
        return False
    
    else:
        # Todo bien
        return True

# --- LÓGICA DE CONTROL DE ACCESO ---
if check_password():
    # AQUÍ VA TODO EL RESTO DE TU CÓDIGO (Títulos, Tablas, Logo, etc.)
    st.success("Bienvenido al sistema")
    # ... todo lo que ya tenemos ...

AZUL_CFJ = "#0169A4"
VERDE_CFJ = "#00B04F"
FONDO_PROFUNDIDAD = "#F4F7F9"
# 2. ESTILO VISUAL (Para que se vea más limpio)
# --- DISEÑO UI/UX AVANZADO ---
st.markdown("""
    <style>
    /* Fondo general con profundidad */
    .stApp {
        background-color: #F4F7F9;
    }
    
    /* Tarjetas blancas con sombra para los datos */
    [data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #00B04F; /* Detalle verde FJ */
    }

    /* Estilo del Editor de Datos (Tabla) */
    .stDataFrame {
        background-color: white;
        padding: 10px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Títulos con fuente más limpia */
    h1, h2, h3 {
        color: #0169A4; /* Azul FJ */
        font-weight: 700;
    }
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
    usuario = st.secrets["db_user"]
    clave = st.secrets["db_password"]
    host = st.secrets["db_host"]
    puerto = st.secrets["db_port"]
    db = st.secrets["db_name"]
    
    url = f"postgresql://{usuario}:{clave}@{host}:{puerto}/{db}"
    return create_engine(url)

# --- 4. CARGA DE DATOS ---
try:
    engine = conectar_db()
    
    # Usamos comillas dobles por las mayúsculas en los nombres de las columnas
    query = """
    SELECT 
        f."Recurso", 
        d."Nombre_Material", 
        d."Unidad",
        f."SALDO_SISTEMA", 
        f."STOCK_FISICO", 
        f."DIFERENCIA_UNIDADES"
    FROM fact_fisico f
    JOIN dim_recurso d ON f."Recurso" = d."Recurso"
    """
    df = pd.read_sql(query, engine)
    
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

# --- 6. TABLA INTERACTIVA Y EDICIÓN ---
    st.subheader("📋 Control de Stock Físico")

df_editado = st.data_editor(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Recurso": st.column_config.TextColumn("ID Recurso", disabled=True),
        "Nombre_Material": st.column_config.TextColumn("Descripción", width="large"),
        "Unidad": st.column_config.TextColumn("U.M.", width="small"),
        "STOCK_FISICO": st.column_config.NumberColumn("Conteo Físico", format="%.2f 🛠️", help="Ingresa el conteo real de bodega"),
        "SALDO_SISTEMA": st.column_config.NumberColumn("Saldo Teórico", disabled=True)
    }
)
    # El botón de guardar debe estar ALINEADO con el st.data_editor
    if st.button("💾 Guardar cambios en SQL"):
        try:
            # Por ahora usamos replace para probar, luego lo afinamos
            df_editado.to_sql('fact_fisico', engine, if_exists='replace', index=False)
            st.success("✅ ¡Base de Datos actualizada! Ya puedes refrescar Power BI.")
            st.balloons()
        except Exception as error_guardado:
            st.error(f"Error al escribir en SQL: {error_guardado}")

except Exception as e:
    # Este es el except que fallaba, asegúrate de que esté alineado al 'try' inicial
    st.error(f"Error de conexión: {e}")

