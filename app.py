import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Despensa Casa", page_icon="🛒", layout="centered")

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def get_gspread_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Crear una copia dict de las credenciales
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # Asegurar que los saltos de línea \n de la private_key estén bien formateados
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=scopes
    )
    return gspread.authorize(credentials)

try:
    gc = get_gspread_client()
    sheet = gc.open("Base Despensa Casa").sheet1
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

# --- CARGAR DATOS ---
def cargar_datos():
    data = sheet.get_all_records()
    df_temp = pd.DataFrame(data)
    if not df_temp.empty and "estado" in df_temp.columns:
        df_temp["estado"] = df_temp["estado"].astype(str).str.strip().replace({"Agotada": "Agotado", "agotada": "Agotado"})
    return df_temp

df = cargar_datos()

st.title("🛒 Control de Despensa Casa")
st.markdown("Lista sincronizada en tiempo real.")

# --- AGREGAR PRODUCTO ---
with st.expander("➕ Agregar nuevo producto a la lista"):
    with st.form("form_agregar"):
        nuevo_nombre = st.text_input("Nombre del producto")
        nueva_categoria = st.selectbox("Categoría", ["Abarrotes", "Lácteos", "Licores", "Limpieza", "Frutas y Verduras", "Otros"])
        quien_agrega = st.text_input("¿Quién lo anota?", value="Iván")
        submitted = st.form_submit_button("Añadir")
        
        if submitted and nuevo_nombre:
            nuevo_id = int(df['id'].max() + 1) if not df.empty and 'id' in df.columns and pd.notna(df['id'].max()) else 1
            nueva_fila = [nuevo_id, nuevo_nombre, nueva_categoria, "Agotado", quien_agrega]
            sheet.append_row(nueva_fila)
            st.success(f"¡{nuevo_nombre} guardado en Google Sheets!")
            st.rerun()

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
            
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.write(f"**{prod['nombre']}**")
            st.caption(f"Categoría: {prod['categoria']} | Por: {prod['quien']}")
        with col2:
            st.write(badge)
        with col3:
            opciones_estado = ["Disponible", "Por agotarse", "Agotado"]
            idx_actual = opciones_estado.index(estado_actual) if estado_actual in opciones_estado else 2
            
            nuevo_estado = st.selectbox("Cambiar", opciones_estado, 
                                        index=idx_actual, 
                                        key=f"status_{prod['id']}", label_visibility="collapsed")
            if nuevo_estado != estado_actual:
                cell = sheet.find(str(prod["id"]))
                sheet.update_cell(cell.row, 4, nuevo_estado)
                st.rerun()
        st.markdown("---")
else:
    st.info("No hay productos registrados aún en 'Base Despensa Casa'.")
