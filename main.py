import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
from utils.email_parser import parse_email_content
from utils.email_reader import EmailReader
from utils.data_manager import (
    load_transactions, save_transaction, load_categories,
    save_categories, load_categories_with_budget,
    update_category_budget, get_budget_history,
    update_category_notes
)
from utils.auth import register_user, validate_login
import os

# Configuración de la página
st.set_page_config(
    page_title="Control de Gastos",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estado de sesión para autenticación
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Estilos CSS personalizados
st.markdown("""
    <style>
        .main {
            padding-top: 2rem;
        }
        .st-emotion-cache-1rtdyuf {
            color: rgb(49, 51, 63);
            font-family: "Source Sans Pro", sans-serif;
        }
        .st-emotion-cache-16idsys p {
            font-size: 1rem;
            font-weight: 400;
        }
        .stButton > button {
            width: 100%;
            border-radius: 8px;
            padding: 0.5rem;
            background-color: #DB7093;
            color: white;
            border: none;
            margin: 0.5rem 0;
            font-size: 1rem;
        }
        .auth-form {
            max-width: 400px;
            margin: 2rem auto;
            padding: 2rem;
            background-color: white;
            border-radius: 16px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .center-text {
            text-align: center;
            margin: 1rem 0;
            color: #666;
        }
        .divider {
            display: flex;
            align-items: center;
            text-align: center;
            margin: 1.5rem 0;
        }
        .divider::before, .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #eee;
        }
        .divider span {
            padding: 0 10px;
            color: #666;
            font-size: 0.9rem;
        }
        .google-btn {
            width: 100%;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 0.5rem;
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        .input-label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.3rem;
        }
        .stTextInput > div > div {
            border-radius: 8px;
            border: 1px solid #ddd;
        }
    </style>
""", unsafe_allow_html=True)

def show_login_page():
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    st.title("Welcome to Finance App")
    st.markdown("Start your financial journey here", unsafe_allow_html=True)

    st.markdown("""
        <button class="google-btn">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" 
                 style="height: 20px; margin-right: 10px;">
            Sign in with Google
        </button>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider"><span>OR CONTINUE WITH</span></div>', unsafe_allow_html=True)

    with st.form("login_form"):
        st.markdown('<p class="input-label">Email</p>', unsafe_allow_html=True)
        email = st.text_input("", placeholder="you@example.com", label_visibility="collapsed")

        st.markdown('<p class="input-label">Password</p>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Enter your password", label_visibility="collapsed")

        submit = st.form_submit_button("Login")

        if submit:
            success, message, user = validate_login(email, password)
            if success:
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.success(f"¡Bienvenido, {user.username}!")
                st.rerun()
            else:
                st.error(message)

    st.markdown('<div class="center-text">', unsafe_allow_html=True)
    st.markdown("Don't have an account?")
    if st.button("Register"):
        st.session_state.show_register = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_register_page():
    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    st.title("Create Account")
    st.markdown("Join us to manage your finances", unsafe_allow_html=True)

    st.markdown("""
        <button class="google-btn">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" 
                 style="height: 20px; margin-right: 10px;">
            Sign up with Google
        </button>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider"><span>OR CONTINUE WITH</span></div>', unsafe_allow_html=True)

    with st.form("register_form"):
        st.markdown('<p class="input-label">Email</p>', unsafe_allow_html=True)
        email = st.text_input("", placeholder="you@example.com", label_visibility="collapsed")

        st.markdown('<p class="input-label">Username</p>', unsafe_allow_html=True)
        username = st.text_input("", placeholder="Choose a username", label_visibility="collapsed")

        st.markdown('<p class="input-label">Password</p>', unsafe_allow_html=True)
        password = st.text_input("", type="password", placeholder="Create a password", label_visibility="collapsed")

        st.markdown('<p class="input-label">Confirm Password</p>', unsafe_allow_html=True)
        password_confirm = st.text_input("", type="password", placeholder="Confirm your password", label_visibility="collapsed")

        submit = st.form_submit_button("Register")

        if submit:
            if password != password_confirm:
                st.error("Las contraseñas no coinciden")
            else:
                success, message = register_user(email, username, password)
                if success:
                    st.success(message)
                    st.session_state.show_register = False
                    st.rerun()
                else:
                    st.error(message)

    st.markdown('<div class="center-text">', unsafe_allow_html=True)
    st.markdown("Already have an account?")
    if st.button("Login"):
        st.session_state.show_register = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Mostrar páginas de autenticación si no hay usuario logueado
if not st.session_state.user_id:
    if not hasattr(st.session_state, 'show_register'):
        st.session_state.show_register = False

    if st.session_state.show_register:
        show_register_page()
    else:
        show_login_page()
    st.stop()

# Si hay usuario logueado, mostrar la aplicación normal
# Función para actualizar las transacciones
def update_transactions():
    print("\n=== Actualizando transacciones ===")
    st.session_state.transactions = load_transactions()
    print(f"Transacciones cargadas: {len(st.session_state.transactions) if not st.session_state.transactions.empty else 0}")

# Inicializar estado de la sesión
if 'categories' not in st.session_state:
    st.session_state.categories = load_categories()
if 'transactions' not in st.session_state:
    update_transactions()
if 'synced_transactions' not in st.session_state:
    st.session_state.synced_transactions = []

# Menú de navegación lateral
with st.sidebar:
    st.title("Control de Gastos")

    # Contenedor para el menú de navegación
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                background-color: #FFFFFF;
                min-width: 250px !important;
            }
            .st-emotion-cache-16idsys p {
                font-size: 1rem !important;
                color: #262730 !important;
            }
            div[role="radiogroup"] > div {
                margin: 0.5rem 0;
                padding: 0.5rem;
                border-radius: 0.5rem;
            }
            div[role="radiogroup"] > div:hover {
                background-color: rgba(151, 166, 195, 0.15);
            }
            .st-emotion-cache-1inwz65 {
                font-size: 1rem;
                font-weight: 400;
                color: #262730;
            }
        </style>
    """, unsafe_allow_html=True)

    menu_options = {
        "🏠 Dashboard": "Dashboard",
        "💰 Ingresar Gasto": "Ingresar Gasto",
        "📧 Sincronizar Correos": "Sincronizar Correos",
        "🏷️ Gestionar Categorías": "Gestionar Categorías",
        "📊 Gestionar Presupuestos": "Gestionar Presupuestos"
    }

    selected = st.radio(
        "Navegación",
        options=list(menu_options.keys()),
        format_func=lambda x: x,
        label_visibility="collapsed",
        key="nav_radio"
    )

    page = menu_options[selected]


# Mapear las opciones del menú a las páginas

if page == "Dashboard":
    st.header("📊 Dashboard de Gastos")

    # Forzar recarga de transacciones
    update_transactions()

    if st.session_state.transactions.empty:
        st.info("No hay transacciones registradas aún.")
    else:
        # Selector de mes y año
        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox(
                "Año",
                options=sorted(st.session_state.transactions['fecha'].dt.year.unique()),
                index=len(st.session_state.transactions['fecha'].dt.year.unique()) - 1,
                key="dashboard_year"
            )
        with col2:
            month = st.selectbox(
                "Mes",
                options=list(range(1, 13)),
                index=datetime.now().month - 1,
                format_func=lambda x: ['Enero', 'Febrero', 'Marzo', 'Abril', 
                                        'Mayo', 'Junio', 'Julio', 'Agosto',
                                        'Septiembre', 'Octubre', 'Noviembre', 
                                        'Diciembre'][x-1],
                key="dashboard_month"
            )

        # Filtrar transacciones por mes y año
        filtered_df = st.session_state.transactions[
            (st.session_state.transactions['fecha'].dt.year == year) &
            (st.session_state.transactions['fecha'].dt.month == month)
        ]

        # Botón para recargar datos
        if st.button("↻ Recargar Datos"):
            update_transactions()
            st.rerun()

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        real_gastos = filtered_df[filtered_df['tipo'] == 'real']['monto'].sum()

        # Obtener presupuestos del mes seleccionado
        fecha_seleccionada = datetime(year, month, 1)
        categories_with_budget = load_categories_with_budget(fecha_seleccionada)
        proy_gastos = sum(float(presupuesto if presupuesto is not None else 0.0) 
                         for _, presupuesto, _ in categories_with_budget)

        # Debug info
        print("\n=== Debug de Gastos ===")
        print(f"Total transacciones: {len(filtered_df)}")
        print(f"Tipos únicos: {filtered_df['tipo'].unique()}")
        print(f"Gastos reales: {real_gastos}")
        print(f"Gastos proyectados: {proy_gastos}")

        with col1:
            st.metric("Total Gastos Reales", f"S/. {real_gastos:.2f}")
        with col2:
            st.metric("Total Gastos Proyectados", f"S/. {proy_gastos:.2f}")
        with col3:
            st.metric("Total General", f"S/. {(real_gastos + proy_gastos):.2f}")
        with col4:
            st.metric("Número de Transacciones", len(filtered_df))

        # Gráfico de barras comparativo
        st.subheader("Comparación por Categoría: Real vs Proyectado")

        # Preparar datos para el gráfico
        real_by_cat = filtered_df[filtered_df['tipo'] == 'real'].groupby('categoria')['monto'].sum()

        # Convertir presupuestos a diccionario
        presupuestos = {cat: float(presup if presup is not None else 0.0) 
                       for cat, presup, _ in categories_with_budget}

        # Crear DataFrame con todas las categorías
        all_categories = sorted(set(list(real_by_cat.index) + list(presupuestos.keys())))

        compare_data = []
        for cat in all_categories:
            compare_data.append({
                'categoria': cat,
                'Real': real_by_cat.get(cat, 0.0),
                'Proyectado': presupuestos.get(cat, 0.0)
            })

        compare_df = pd.DataFrame(compare_data)

        # Convertir de formato ancho a largo para el gráfico
        compare_df_long = pd.melt(
            compare_df, 
            id_vars=['categoria'],
            value_vars=['Real', 'Proyectado'],
            var_name='Tipo',
            value_name='Monto'
        )

        # Crear gráfico de barras
        fig = px.bar(
            compare_df_long,
            x='categoria',
            y='Monto',
            color='Tipo',
            title='Gastos Reales vs Proyectados por Categoría',
            barmode='group',
            labels={'categoria': 'Categoría', 'Monto': 'Monto (S/.)'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig)

        # Transactions table
        st.subheader("Listado de Transacciones")
        if not filtered_df.empty:
            # Formatear la fecha para mostrar
            display_df = filtered_df.copy()
            display_df['fecha'] = display_df['fecha'].dt.strftime('%Y-%m-%d %H:%M')
            # Ordenar por fecha más reciente y mostrar el tipo de transacción
            display_df = display_df.sort_values('fecha', ascending=False)
            st.dataframe(
                display_df,
                column_order=['fecha', 'monto', 'descripcion', 'categoria', 'tipo', 'moneda'],
                column_config={
                    'fecha': 'Fecha',
                    'monto': st.column_config.NumberColumn('Monto', format="S/. %.2f"),
                    'descripcion': 'Descripción',
                    'categoria': 'Categoría',
                    'tipo': st.column_config.SelectboxColumn(
                        'Tipo',
                        options=['real', 'proyectado'],
                        required=True
                    ),
                    'moneda': 'Moneda'
                }
            )
        else:
            st.info("No hay transacciones para mostrar en el período seleccionado")

        # Export button
        if st.button("Exportar Datos"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name=f"transacciones_{year}_{month}.csv",
                mime="text/csv"
            )

elif page == "Ingresar Gasto":
    st.header("💰 Nuevo Gasto")

    # Formulario para nuevo gasto con diseño mejorado
    with st.form("nuevo_gasto", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            fecha = st.date_input("📅 Fecha")
            monto = st.number_input("💵 Monto (S/.)", min_value=0.0, step=0.1)

        with col2:
            descripcion = st.text_input("📝 Descripción")
            categoria = st.selectbox("🏷️ Categoría", options=st.session_state.categories)

        tipo = st.radio("Tipo de Gasto", ['real', 'proyectado'], 
                       format_func=lambda x: "💳 Real" if x == 'real' else "📅 Proyectado")

        submitted = st.form_submit_button("💾 Guardar Gasto")

        if submitted:
            transaction = {
                'fecha': fecha,
                'monto': monto,
                'descripcion': descripcion,
                'categoria': categoria,
                'tipo': tipo,
                'moneda': 'PEN'
            }
            if save_transaction(transaction):
                update_transactions()
                st.success("✅ ¡Gasto guardado exitosamente!")
                st.rerun()
            else:
                st.error("❌ Error al guardar el gasto")

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
                                    update_transactions()
                                    st.success("¡Transacción guardada exitosamente!")
                                    st.rerun()
                                else:
                                    st.error("Error: No se pudo guardar la transacción")

                            except Exception as e:
                                print(f"Error guardando transacción: {str(e)}")
                                st.error(f"Error inesperado: {str(e)}")

                        if st.button("❌ Descartar", key=f"discard_{idx}"):
                            # Remove discarded transaction from session state
                            st.session_state.synced_transactions.pop(idx)
                            st.success("Transacción descartada")
                            st.rerun()

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

elif page == "Gestionar Presupuestos":
    st.title("Gestionar Presupuestos Mensuales")

    st.info("""
    Aquí puedes configurar el presupuesto mensual para cada categoría.
    Los presupuestos se mantienen en un histórico, permitiendo ver la evolución 
    a lo largo del tiempo.
    """)

    # Selector de mes y año
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox(
            "Año",
            options=list(range(2024, 2026)),
            index=datetime.now().year - 2024
        )
    with col2:
        month = st.selectbox(
            "Mes",
            options=list(range(1, 13)),
            index=datetime.now().month - 1,
            format_func=lambda x: ['Enero', 'Febrero', 'Marzo', 'Abril', 
                                    'Mayo', 'Junio', 'Julio', 'Agosto',
                                    'Septiembre', 'Octubre', 'Noviembre', 
                                    'Diciembre'][x-1]
        )

    # Crear fecha del primer día del mes seleccionado
    fecha_seleccionada = datetime(year, month, 1)

    # Cargar categorías con sus presupuestos para el mes seleccionado
    categories_with_budget = load_categories_with_budget(fecha_seleccionada)

    # Calcular presupuesto total
    total_budget = sum(float(presupuesto if presupuesto is not None else 0.0) 
                      for _, presupuesto, _ in categories_with_budget)

    # Crear DataFrame para el gráfico de barras
    df_budget = pd.DataFrame([
        {'Categoría': cat, 'Presupuesto': float(presup if presup is not None else 0.0)}
        for cat, presup, _ in categories_with_budget
    ])

    # Gráfico de barras
    fig = px.bar(
        df_budget,
        x='Categoría',
        y='Presupuesto',
        title='Presupuesto por Categoría',
        labels={'Presupuesto': 'Monto (S/.)'}
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig)

    # Mostrar métricas de resumen
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Presupuesto Total Mensual", f"S/. {total_budget:.2f}")
    with col2:
        st.metric("Promedio por Categoría", 
                 f"S/. {(total_budget/len(categories_with_budget) if categories_with_budget else 0):.2f}")
    with col3:
        st.metric("Número de Categorías", len(categories_with_budget))

    st.divider()

    # Mostrar formulario para cada categoría
    for categoria, presupuesto, notas in categories_with_budget:
        presupuesto_actual = float(presupuesto if presupuesto is not None else 0.0)
        with st.expander(f"📊 {categoria} - S/. {presupuesto_actual:.2f}", expanded=True):
            col1, col2 = st.columns([2, 1])

            with col1:
                # Mostrar y editar notas
                new_notes = st.text_area(
                    "Notas (describe qué incluye esta categoría)",
                    value=notas if notas else "",
                    key=f"notes_{categoria}",
                    height=100
                )

            with col2:
                # Campo de presupuesto
                nuevo_presupuesto = st.number_input(
                    "Presupuesto mensual",
                    value=presupuesto_actual,
                    step=10.0,
                    key=f"budget_{categoria}"
                )

            if st.button("💾 Actualizar y Guardar", key=f"update_{categoria}"):
                print(f"\n=== Intentando actualizar {categoria} ===")
                print(f"Nuevo presupuesto: {nuevo_presupuesto}")
                print(f"Fecha seleccionada: {fecha_seleccionada}")

                # Actualizar el presupuesto
                updated_budget = update_category_budget(categoria, nuevo_presupuesto, fecha_seleccionada)
                updated_notes = update_category_notes(categoria, new_notes)

                if updated_budget and updated_notes:
                    st.success("✅ Presupuesto y notas actualizados")
                    st.session_state.clear()  # Limpiar el estado para forzar recarga
                    st.rerun()
                else:
                    st.error("❌ Error al actualizar los datos")