
# GastoSync - Aplicación de Gestión Financiera Personal

Una aplicación web moderna para el seguimiento y control de gastos personales, con sincronización automática de notificaciones bancarias BCP.

## Características Principales

- 📊 Dashboard interactivo con visualización de gastos
- 💰 Registro manual y automático de transacciones
- 📧 Sincronización con notificaciones de correo BCP
- 🏷️ Sistema de categorización de gastos
- 💼 Gestión de presupuestos mensuales
- 📈 Histórico de gastos y presupuestos
- 🔐 Sistema de autenticación de usuarios

## Requisitos Técnicos

- Python 3.11+
- PostgreSQL 16
- Streamlit 1.42+
- SQLAlchemy 2.0+

## Estructura del Proyecto

```
├── utils/                  # Utilidades y módulos
│   ├── auth.py            # Autenticación de usuarios
│   ├── data_manager.py    # Gestión de datos
│   ├── database.py        # Configuración de base de datos
│   ├── email_parser.py    # Parseador de correos
│   └── email_reader.py    # Lector de correos
├── main.py                # Aplicación principal
└── test_app_flow.py       # Tests de flujo
```

## Configuración

1. Configurar variables de entorno:
   ```
   DATABASE_URL=postgresql://user:pass@host/db
   ```

2. Inicializar base de datos:
   ```python
   python utils/migrate_data.py
   ```

3. Ejecutar la aplicación:
   ```python
   streamlit run main.py
   ```
   
