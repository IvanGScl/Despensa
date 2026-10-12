import streamlit as st
import datetime

st.set_page_config(page_title="Despensa del Hogar", page_icon="🛒", layout="centered")

if 'productos' not in st.session_state:
    st.session_state.productos = [
        {"id": 1, "nombre": "Leche entera", "categoria": "Lácteos", "estado": "Agotado", "quien": "Mamá"},
        {"id": 2, "nombre": "Detergente líquido", "categoria": "Limpieza", "estado": "Por agotarse", "quien": "Papá"},
        {"id": 3, "nombre": "Huevos", "categoria": "Abarrotes", "estado": "Disponible", "quien": "Hijo"},
        {"id": 4, "nombre": "Papel higiénico", "categoria": "Limpieza", "estado": "Agotado", "quien": "Mamá"},
    ]

st.title("🛒 Control de Despensa y Compras del Hogar")
st.markdown("Indica qué productos se están acabando o ya se agotaron para que todos puedan verlo.")

with st.expander("➕ Agregar nuevo producto a la lista"):
    with st.form("form_agregar"):
        nuevo_nombre = st.text_input("Nombre del producto")
        nueva_categoria = st.selectbox("Categoría", ["Abarrotes", "Lácteos", "Limpieza", "Frutas y Verduras", "Otros"])
        quien_agrega = st.text_input("¿Quién lo anota?", value="Integrante")
        submitted = st.form_submit_button("Añadir")

        if submitted and nuevo_nombre:
            nuevo_id = max([p["id"] for p in st.session_state.productos]) + 1 if st.session_state.productos else 1
            st.session_state.productos.append({
                "id": nuevo_id,
                "nombre": nuevo_nombre,
                "categoria": nueva_categoria,
                "estado": "Agotado",
                "quien": quien_agrega
            })
            st.success(f"¡{nuevo_nombre} agregado exitosamente!")
            st.rerun()

st.divider()

filtro_estado = st.radio("Filtrar por estado:", ["Todos", "🔴 Agotados", "🟡 Por agotarse", "🟢 Disponibles"], horizontal=True)

st.subheader("📋 Estado actual de la despensa")
estado_map = {"🔴 Agotados": "Agotado", "🟡 Por agotarse": "Por agotarse", "🟢 Disponibles": "Disponible"}

for prod in st.session_state.productos:
    if filtro_estado != "Todos" and prod["estado"] != estado_map[filtro_estado]:
        continue

    if prod["estado"] == "Agotado":
        badge = "🔴 **AGOTADO**"
    elif prod["estado"] == "Por agotarse":
        badge = "🟡 **POR AGOTARSE**"
    else:
        badge = "🟢 **DISPONIBLE**"

    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        st.write(f"**{prod['nombre']}**")
        st.caption(f"Categoría: {prod['categoria']} | Reportado por: {prod['quien']}")
    with col2:
        st.write(badge)
    with col3:
        nuevo_estado = st.selectbox("Cambiar", ["Disponible", "Por agotarse", "Agotado"], 
                                    index=["Disponible", "Por agotarse", "Agotado"].index(prod["estado"]), 
                                    key=f"status_{prod['id']}", label_visibility="collapsed")
        if nuevo_estado != prod["estado"]:
            prod["estado"] = nuevo_estado
            st.rerun()
    st.markdown("---")

agotados_count = sum(1 for p in st.session_state.productos if p["estado"] == "Agotado")
por_agotarse_count = sum(1 for p in st.session_state.productos if p["estado"] == "Por agotarse")
st.info(f"💡 Resumen para compras: Hay **{agotados_count}** productos agotados y **{por_agotarse_count}** por agotarse.")
