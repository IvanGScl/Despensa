import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Despensa Casa", page_icon="🛒", layout="centered")

SHEET_ID = "16DC78ghtTbajAxo5PNeQ4AawZrJGqDSwikAQAQSHLjw"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&id={SHEET_ID}&gid=0"

# PEGA AQUÍ LA URL DE TU WEB APP DE APPS SCRIPT
APPS_SCRIPT_URL = "APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzB72A7wgdZ3oZ5SRpzzPX9cyye_a-k5hoynXYmYzTE1gNeHHYsyppFziLo8x8LsE5l/exec""

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
st.markdown("Lista sincronizada en tiempo real (Sin claves ni secretos).")

# --- AGREGAR PRODUCTO (AUTOMÁTICO VÍA WEB APP) ---
with st.expander("➕ Agregar nuevo producto a la lista"):
    with st.form("form_agregar", clear_on_submit=True):
        nuevo_nombre = st.text_input("Nombre del producto")
        nueva_categoria = st.selectbox("Categoría", ["Abarrotes", "Lácteos", "Licores", "Limpieza", "Frutas y Verduras", "Otros"])
        quien_agrega = st.text_input("¿Quién lo anota?", value="Iván")
        submitted = st.form_submit_button("Añadir a la Despensa")
        
        if submitted and nuevo_nombre:
            nuevo_id = int(df['id'].max() + 1) if not df.empty and 'id' in df.columns and pd.notna(df['id'].max()) else 1
            
            payload = {
                "action": "append",
                "id": nuevo_id,
                "nombre": nuevo_nombre,
                "categoria": nueva_categoria,
                "estado": "Agotado",
                "quien": quien_agrega
            }
            
            try:
                response = requests.post(APPS_SCRIPT_URL, json=payload)
                if response.status_code == 200:
                    st.success(f"¡'{nuevo_nombre}' agregado correctamente!")
                    st.rerun()
                else:
                    st.error("Error al comunicarse con la hoja.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

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
                payload = {
                    "action": "update",
                    "id": int(prod["id"]),
                    "estado": nuevo_estado
                }
                requests.post(APPS_SCRIPT_URL, json=payload)
                st.rerun()
        st.markdown("---")
else:
    st.info("No hay productos registrados aún en la despensa.")
