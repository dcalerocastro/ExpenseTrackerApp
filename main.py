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
if 'synced_transactions' not in st.session_state:
    st.session_state.synced_transactions = []

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
                        color='tipo')
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
    if not filtered_df.empty:
        # Formatear la fecha para mostrar
        display_df = filtered_df.copy()
        display_df['fecha'] = display_df['fecha'].dt.strftime('%Y-%m-%d')
        # Ordenar por fecha más reciente
        display_df = display_df.sort_values('fecha', ascending=False)
        st.dataframe(display_df)
    else:
        st.info("No hay transacciones para mostrar en el período seleccionado")

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

    st.info("""
    Para sincronizar tus notificaciones del BCP, necesitas configurar tu cuenta de Gmail.
    La aplicación solo leerá los correos de notificaciones del BCP.
    """)

    # Formulario de configuración de Gmail
    with st.form("gmail_config"):
        email = st.text_input("Correo Gmail", value=os.getenv('EMAIL_USER', ''))
        password = st.text_input("Contraseña de Aplicación", type="password", 
                               help="Contraseña de 16 caracteres generada por Google")

        st.markdown("""
        ### ¿Cómo obtener la Contraseña de Aplicación?
        1. Ve a [Configuración de Seguridad de Google](https://myaccount.google.com/security)
        2. Activa la "Verificación en dos pasos" si no está activada
        3. Busca "Contraseñas de aplicación" (casi al final de la página)
        4. Selecciona "Otra" y nombra la app como "Streamlit App"
        5. Copia la contraseña de 16 caracteres que Google te genera
        """)

        submit_creds = st.form_submit_button("Guardar Credenciales")

        if submit_creds and email and password:
            try:
                os.environ['EMAIL_USER'] = email
                os.environ['EMAIL_PASSWORD'] = password
                st.success("¡Credenciales guardadas! Ahora puedes sincronizar tus notificaciones.")
            except Exception as e:
                st.error(f"Error al guardar credenciales: {str(e)}")

    # Only show sync button if credentials are configured
    if os.getenv('EMAIL_USER') and os.getenv('EMAIL_PASSWORD'):
        st.divider()
        days_back = st.slider("Días hacia atrás para buscar", 1, 90, 30)

        if st.button("Sincronizar Notificaciones"):
            try:
                with st.spinner('Conectando con el servidor de correo...'):
                    reader = EmailReader(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
                    transactions = reader.fetch_bcp_notifications(days_back)

                    if transactions:
                        st.success(f"Se encontraron {len(transactions)} notificaciones")
                        # Store transactions in session state
                        st.session_state.synced_transactions = transactions
                    else:
                        st.warning("No se encontraron notificaciones en el período seleccionado")

            except Exception as e:
                st.error(f"Error al sincronizar: {str(e)}")

        # Display synced transactions
        if st.session_state.synced_transactions:
            st.subheader(f"Transacciones Pendientes ({len(st.session_state.synced_transactions)})")

            for idx, transaction in enumerate(st.session_state.synced_transactions):
                with st.expander(f"Transacción: {transaction['descripcion']} - S/. {transaction['monto']:.2f}", expanded=True):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"📅 Fecha: {transaction['fecha'].strftime('%d/%m/%Y')}")
                        st.write(f"💰 Monto: S/. {transaction['monto']:.2f}")
                        st.write(f"📝 Descripción: {transaction['descripcion']}")

                        # Agregar categoría a la transacción
                        transaction['categoria'] = st.selectbox(
                            "🏷️ Categoría",
                            options=st.session_state.categories,
                            key=f"cat_{idx}"
                        )

                    with col2:
                        if st.button("💾 Guardar", key=f"save_{idx}"):
                            try:
                                # Crear una copia de la transacción para no modificar el original
                                save_data = {
                                    'fecha': transaction['fecha'],
                                    'monto': float(transaction['monto']),
                                    'descripcion': transaction['descripcion'],
                                    'categoria': transaction['categoria'],
                                    'tipo': 'real',
                                    'moneda': transaction.get('moneda', 'PEN')
                                }

                                print(f"\n=== Guardando transacción {idx} ===")
                                print(f"Datos a guardar: {save_data}")

                                if save_transaction(save_data):
                                    # Remove saved transaction from session state
                                    st.session_state.synced_transactions.pop(idx)
                                    # Recargar las transacciones para actualizar la vista
                                    st.session_state.transactions = load_transactions()
                                    st.success("¡Transacción guardada exitosamente!")
                                else:
                                    st.error("Error: No se pudo guardar la transacción")

                            except Exception as e:
                                print(f"Error guardando transacción: {str(e)}")
                                st.error(f"Error inesperado: {str(e)}")

                        if st.button("❌ Descartar", key=f"discard_{idx}"):
                            # Remove discarded transaction from session state
                            st.session_state.synced_transactions.pop(idx)
                            st.success("Transacción descartada")

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