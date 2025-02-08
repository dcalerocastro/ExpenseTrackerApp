import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
from utils.email_parser import parse_email_content
from utils.email_reader import EmailReader
from utils.data_manager import (
    load_transactions,
    save_transaction,
    load_categories,
    save_categories
)
import os

# Page config
st.set_page_config(page_title="Seguimiento de Gastos", layout="wide")

# Initialize session state
if 'categories' not in st.session_state:
    st.session_state.categories = load_categories()
if 'transactions' not in st.session_state:
    st.session_state.transactions = load_transactions()

# Sidebar navigation
st.sidebar.title("Navegación")
page = st.sidebar.radio("Ir a", ["Dashboard", "Ingresar Gasto", "Sincronizar Correos", "Gestionar Categorías"])

if page == "Dashboard":
    st.title("Dashboard de Gastos")

    # Date filters
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha inicial", 
                                min(st.session_state.transactions['fecha']) if not st.session_state.transactions.empty else datetime.now())
    with col2:
        end_date = st.date_input("Fecha final", 
                                max(st.session_state.transactions['fecha']) if not st.session_state.transactions.empty else datetime.now())

    filtered_df = st.session_state.transactions[
        (st.session_state.transactions['fecha'] >= pd.Timestamp(start_date)) &
        (st.session_state.transactions['fecha'] <= pd.Timestamp(end_date))
    ]

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    real_gastos = filtered_df[filtered_df['tipo'] == 'real']['monto'].sum()
    proy_gastos = filtered_df[filtered_df['tipo'] == 'proyectado']['monto'].sum()

    with col1:
        st.metric("Total Gastos Reales", f"S/. {real_gastos:.2f}")
    with col2:
        st.metric("Total Gastos Proyectados", f"S/. {proy_gastos:.2f}")
    with col3:
        st.metric("Total General", f"S/. {(real_gastos + proy_gastos):.2f}")
    with col4:
        st.metric("Número de Transacciones", len(filtered_df))

    # Visualizations
    col1, col2 = st.columns(2)

    with col1:
        # Pie chart by category
        fig_pie = px.pie(filtered_df, 
                        values='monto', 
                        names='categoria',
                        title='Distribución de Gastos por Categoría',
                        color='tipo')  # Diferenciar por tipo
        st.plotly_chart(fig_pie)

    with col2:
        # Time series of expenses
        fig_line = go.Figure()

        # Gastos reales
        real_daily = filtered_df[filtered_df['tipo'] == 'real'].groupby('fecha')['monto'].sum().reset_index()
        fig_line.add_trace(go.Scatter(x=real_daily['fecha'], y=real_daily['monto'],
                                    name='Gastos Reales',
                                    line=dict(color='blue')))

        # Gastos proyectados
        proy_daily = filtered_df[filtered_df['tipo'] == 'proyectado'].groupby('fecha')['monto'].sum().reset_index()
        fig_line.add_trace(go.Scatter(x=proy_daily['fecha'], y=proy_daily['monto'],
                                    name='Gastos Proyectados',
                                    line=dict(color='red', dash='dash')))

        fig_line.update_layout(title='Gastos Diarios - Reales vs Proyectados')
        st.plotly_chart(fig_line)

    # Transactions table
    st.subheader("Listado de Transacciones")
    st.dataframe(filtered_df)

    # Export button
    if st.button("Exportar Datos"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Descargar CSV",
            data=csv,
            file_name="transacciones.csv",
            mime="text/csv"
        )

elif page == "Ingresar Gasto":
    st.title("Ingresar Nuevo Gasto")

    # Formulario para nuevo gasto
    with st.form("nuevo_gasto"):
        col1, col2 = st.columns(2)

        with col1:
            fecha = st.date_input("Fecha")
            monto = st.number_input("Monto (S/.)", min_value=0.0, step=0.1)

        with col2:
            descripcion = st.text_input("Descripción")
            categoria = st.selectbox("Categoría", options=st.session_state.categories)

        tipo = st.radio("Tipo de Gasto", ['real', 'proyectado'])

        submitted = st.form_submit_button("Guardar Gasto")

        if submitted:
            transaction = {
                'fecha': fecha,
                'monto': monto,
                'descripcion': descripcion,
                'categoria': categoria,
                'tipo': tipo
            }
            save_transaction(transaction)
            st.session_state.transactions = load_transactions()
            st.success("¡Gasto guardado exitosamente!")

elif page == "Sincronizar Correos":
    st.title("Sincronización de Notificaciones BCP")

    # Verificar credenciales
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')

    if not email_user or not email_password:
        st.error("No se han configurado las credenciales de correo. Por favor, contacta al administrador.")
        st.info("""
        Para configurar el acceso a Gmail, necesitas:
        1. Una cuenta de Gmail con verificación en dos pasos activada
        2. Una contraseña de aplicación específica:
           - Ve a https://myaccount.google.com/security
           - Busca "Contraseñas de aplicación"
           - Genera una nueva para "Streamlit App"
        """)
    else:
        st.info(f"Configurado para la cuenta: {email_user}")
        days_back = st.slider("Días hacia atrás para buscar", 1, 90, 30)

        if st.button("Sincronizar Notificaciones"):
            try:
                with st.spinner('Conectando con el servidor de correo...'):
                    reader = EmailReader(email_user, email_password)
                    transactions = reader.fetch_bcp_notifications(days_back)

                    if transactions:
                        st.success(f"Se encontraron {len(transactions)} notificaciones")

                        # Mostrar transacciones encontradas
                        for transaction in transactions:
                            with st.expander(f"Transacción: {transaction['descripcion']} - {transaction['fecha'].strftime('%Y-%m-%d')}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    transaction['fecha'] = st.date_input("Fecha", transaction['fecha'], key=f"date_{id(transaction)}")
                                    transaction['monto'] = st.number_input("Monto", value=float(transaction['monto']), key=f"amount_{id(transaction)}")
                                with col2:
                                    transaction['descripcion'] = st.text_input("Descripción", transaction['descripcion'], key=f"desc_{id(transaction)}")
                                    transaction['categoria'] = st.selectbox("Categoría", options=st.session_state.categories, key=f"cat_{id(transaction)}")

                                transaction['tipo'] = 'real'  # Las transacciones del banco son siempre reales

                                if st.button("Guardar", key=f"save_{id(transaction)}"):
                                    save_transaction(transaction)
                                    st.session_state.transactions = load_transactions()
                                    st.success("Transacción guardada exitosamente!")
                    else:
                        st.warning("No se encontraron notificaciones en el período seleccionado. Verifica que:")
                        st.markdown("""
                        1. Tu cuenta tenga correos del BCP con el asunto exacto
                        2. Los correos estén dentro del período seleccionado
                        3. La contraseña de aplicación sea correcta
                        """)
            except Exception as e:
                st.error(f"Error al sincronizar: {str(e)}")

elif page == "Gestionar Categorías":
    st.title("Gestionar Categorías")

    # Add new category
    new_category = st.text_input("Nueva Categoría")
    if st.button("Agregar Categoría"):
        if new_category and new_category not in st.session_state.categories:
            st.session_state.categories.append(new_category)
            save_categories(st.session_state.categories)
            st.success(f"Categoría '{new_category}' agregada!")
        else:
            st.error("Categoría inválida o ya existe")

    # List current categories
    st.subheader("Categorías Actuales")
    for category in st.session_state.categories:
        st.write(f"- {category}")