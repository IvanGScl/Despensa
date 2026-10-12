import streamlit as st
import pandas as pd

st.set_page_config(page_title="Despensa Casa", page_icon="🛒", layout="centered")

# --- CONEXIÓN NATIVA A GOOGLE SHEETS ---
try:
    # Utiliza la conexión nativa integrada en Streamlit
    conn = st.connection("gsheets", type="gsheets")
    # Lee la hoja de cálculo por defecto
    df = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/16DC78ghtTbajAxo5PNeQ4AawZrJGqDSwikAQAQSHLjw/edit", ttl=0)
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

st.title("🛒 Control de Despensa Casa")
st.markdown("Lista sincronizada en tiempo real.")

# Normalizar columnas si es necesario
if not df.empty and "estado" in df.columns:
    df["estado"] = df["estado"].astype(str).str.strip().replace({"Agotada": "Agotado", "agotada": "Agotado"})

# --- AGREGAR PRODUCTO ---
with st.expander("➕ Agregar nuevo producto a la lista"):
    with st.form("form_agregar"):
        nuevo_nombre = st.text_input("Nombre del producto")
        nueva_categoria = st.selectbox("Categoría", ["Abarrotes", "Lácteos", "Licores", "Limpieza", "Frutas y Verduras", "Otros"])
        quien_agrega = st.text_input("¿Quién lo anota?", value="Iván")
        submitted = st.form_submit_button("Añadir")
        
        if submitted and nuevo_nombre:
            nuevo_id = int(df['id'].max() + 1) if not df.empty and 'id' in df.columns and pd.notna(df['id'].max()) else 1
            nueva_fila = pd.DataFrame([{"id": nuevo_id, "nombre": nuevo_nombre, "categoria": nueva_categoria, "estado": "Agotado", "quien": quien_agrega}])
            
            # Agregar al DataFrame y actualizar la hoja completa
            df_updated = pd.concat([df, nueva_fila], ignore_index=True)
            conn.update(spreadsheet="https://docs.google.com/spreadsheets/d/16DC78ghtTbajAxo5PNeQ4AawZrJGqDSwikAQAQSHLjw/edit", data=df_updated)
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
                df.at[index, "estado"] = nuevo_estado
                conn.update(spreadsheet="https://docs.google.com/spreadsheets/d/16DC78ghtTbajAxo5PNeQ4AawZrJGqDSwikAQAQSHLjw/edit", data=df)
                st.rerun()
        st.markdown("---")
else:
    st.info("No hay productos registrados aún en 'Base Despensa Casa'.")
