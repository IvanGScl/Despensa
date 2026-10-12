import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Despensa Casa", page_icon="🛒", layout="centered")

# ID de tu Google Sheet y URL de exportación CSV abierta
SHEET_ID = "16DC78ghtTbajAxo5PNeQ4AawZrJGqDSwikAQAQSHLjw"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&id={SHEET_ID}&gid=0"

@st.cache_data(ttl=5)
def cargar_datos():
    try:
        df_temp = pd.read_csv(SHEET_URL)
        # Limpiar nombres de columnas por si acaso
        df_temp.columns = df_temp.columns.str.strip().str.lower()
        if not df_temp.empty and "estado" in df_temp.columns:
            df_temp["estado"] = df_temp["estado"].astype(str).str.strip().replace({"Agotada": "Agotado", "agotada": "Agotado"})
        return df_temp
    except Exception as e:
        st.error(f"Error al leer la hoja de cálculo: {e}")
        return pd.DataFrame()

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
            
            # Enlace directo al formulario de Google Sheets prellenado o aviso de registro
            st.success(f"¡Producto '{nuevo_nombre}' listo! Anótalo directamente en tu planilla abierta.")
            st.markdown(f"👉 [Abrir Google Sheet para editar]({f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit'})")
            st.info(f"Copia esta fila en tu hoja: ID: **{nuevo_id}** | Nombre: **{nuevo_nombre}** | Categoría: **{nueva_categoria}** | Estado: **Agotado** | Quién: **{quien_agrega}**")

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
    st.info("No hay productos registrados aún o la hoja está vacía.")

st.markdown(f"🔗 [Ver planilla original de Google Sheets](https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit)")
