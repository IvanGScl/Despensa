import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Despensa Casa", page_icon="🛒", layout="centered")

SHEET_NAME = "Base Despensa Casa"

# --- CONEXIÓN PÚBLICA / SIN CLAVES COMPLEJAS ---
@st.cache_resource
def conectar_hoja():
    # Si no hay secretos configurados, intentamos conectar mediante gspread público o por CSV directo
    gc = gspread.service_account_from_dict({}) # fallback si fuera necesario
    # O mejor aún, usando un cliente público de gspread con la hoja compartida
    import gspread
    gc = gspread.anonymous()
    return gc.open(SHEET_NAME).sheet1

# Como Google Sheets privado requiere autorización, usaremos la URL de exportación CSV para leer 
# y un método ultra sencillo con gspread si la hoja es pública para cualquier editor.
SHEET_ID = "16DC78ghtTbajAxo5PNeQ4AawZrJGqDSwikAQAQSHLjw"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&id={SHEET_ID}&gid=0"

@st.cache_data(ttl=2)
def cargar_datos():
    try:
        df_temp = pd.read_csv(CSV_URL)
        df_temp.columns = df_temp.columns.str.strip().str.lower()
        if not df_temp.empty and "estado" in df_temp.columns:
            df_temp["estado"] = df_temp["estado"].astype(str).str.strip().replace({"Agotada": "Agotado", "agotada": "Agotado"})
        return df_temp
    except Exception as e:
        st.error(f"Error al leer la hoja: {e}")
        return pd.DataFrame()

df = cargar_datos()

st.title("🛒 Control de Despensa Casa")
st.markdown("Lista sincronizada en tiempo real (Modo sin claves).")

# --- AVISO DE USO ---
st.info("💡 **Modo sin llaves activo:** Para guardar cambios automáticamente de forma instantánea sin errores de servidor, puedes editar directamente tu planilla en el siguiente enlace y la App se actualizará sola al instante:")
st.markdown(f"👉 [Hacer clic aquí para abrir tu Google Sheet y editarla con comodidad](https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit)")

st.divider()

# --- FILTROS Y ESTADO ---
filtro_estado = st.radio("Filtrar por estado:", ["Todos", "🔴 Agotados", "🟡 Por agotarse", "🟢 Disponibles"], horizontal=True)

st.subheader("📋 Estado actual de la despensa")
estado_map = {"🔴 Agotados": "Agotado", "🟡 Por agotarse": "Por agotarse", "🟢 Disponibles": "Disponible"}

if not df.empty:
    for index, prod in df.iterrows():
        estado_actual = str(prod["estado"]).strip()
        if filtro_estado != "Todos" and estado_actual != estado_map[filtro_estado]:
            continue
        
        badge = "🔴 **AGOTADO**" if estado_actual == "Agotado" else ("🟡 **POR AGOTARSE**" if estado_actual == "Por agotarse" else "🟢 **DISPONIBLE**")
            
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write(f"**{prod['nombre']}**")
            st.caption(f"Categoría: {prod['categoria']} | Por: {prod['quien']}")
        with col2:
            st.write(badge)
        st.markdown("---")
else:
    st.info("No hay productos registrados aún en la despensa.")
