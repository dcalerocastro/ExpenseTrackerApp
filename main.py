import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
from utils.email_parser import parse_email_content
from utils.data_manager import (
    load_transactions,
    save_transaction,
    load_categories,
    save_categories
)

# Page config
st.set_page_config(page_title="Seguimiento de Gastos", layout="wide")

# Initialize session state
if 'categories' not in st.session_state:
    st.session_state.categories = load_categories()
if 'transactions' not in st.session_state:
    st.session_state.transactions = load_transactions()

# Sidebar navigation
st.sidebar.title("Navegación")
page = st.sidebar.radio("Ir a", ["Dashboard", "Cargar Emails", "Gestionar Categorías"])

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
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Gastos", f"S/. {filtered_df['monto'].sum():.2f}")
    with col2:
        st.metric("Promedio por Transacción", f"S/. {filtered_df['monto'].mean():.2f}")
    with col3:
        st.metric("Número de Transacciones", len(filtered_df))
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart by category
        fig_pie = px.pie(filtered_df, 
                        values='monto', 
                        names='categoria',
                        title='Distribución de Gastos por Categoría')
        st.plotly_chart(fig_pie)
    
    with col2:
        # Time series of expenses
        daily_expenses = filtered_df.groupby('fecha')['monto'].sum().reset_index()
        fig_line = px.line(daily_expenses, 
                          x='fecha', 
                          y='monto',
                          title='Gastos Diarios')
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

elif page == "Cargar Emails":
    st.title("Cargar Notificaciones de Email")
    
    uploaded_file = st.file_uploader("Cargar archivo de email (.eml)", type=['eml'])
    
    if uploaded_file:
        email_content = uploaded_file.read().decode()
        transaction = parse_email_content(email_content)
        
        if transaction:
            st.subheader("Información Extraída")
            
            col1, col2 = st.columns(2)
            with col1:
                transaction['fecha'] = st.date_input("Fecha", transaction['fecha'])
                transaction['monto'] = st.number_input("Monto", value=float(transaction['monto']))
            with col2:
                transaction['descripcion'] = st.text_input("Descripción", transaction['descripcion'])
                transaction['categoria'] = st.selectbox("Categoría", options=st.session_state.categories)
            
            if st.button("Guardar Transacción"):
                save_transaction(transaction)
                st.session_state.transactions = load_transactions()
                st.success("Transacción guardada exitosamente!")
        else:
            st.error("No se pudo extraer información del email")

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
