
# GastoSync 💰

Una aplicación web moderna para el seguimiento y control de gastos personales, con sincronización automática de notificaciones bancarias BCP.

## 🚀 Características

- 📊 Dashboard interactivo de gastos
- 🔄 Sincronización automática con correos BCP
- 📱 Interfaz responsive y amigable
- 🏷️ Categorización inteligente de gastos
- 📈 Gráficos y estadísticas detalladas
- 🔐 Autenticación segura
- 💾 Base de datos PostgreSQL
- 🌐 Despliegue sencillo en Replit

## 🛠️ Tecnologías

- **Frontend:** Streamlit
- **Backend:** Python 3.11+
- **Base de datos:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0+
- **Autenticación:** Werkzeug
- **Visualización:** Plotly
- **Email:** Google API

## 📁 Estructura del Proyecto

```
├── utils/
│   ├── auth.py          # Sistema de autenticación
│   ├── data_manager.py  # Gestión de datos y transacciones
│   ├── database.py      # Configuración de PostgreSQL
│   ├── email_parser.py  # Parser de correos BCP
│   ├── email_reader.py  # Lector de correos
│   ├── encryption.py    # Manejo de encriptación
│   └── migrate_data.py  # Migración de datos
├── main.py              # Aplicación principal
└── test_app_flow.py     # Tests de funcionalidad
```

## 🚀 Configuración

1. **Variables de Entorno**
   ```
   DATABASE_URL=postgresql://user:pass@host/db
   EMAIL_ACCOUNT=your-email@gmail.com
   ```

2. **Base de Datos**
   ```bash
   python utils/migrate_data.py
   ```

3. **Iniciar Aplicación**
   ```bash
   streamlit run main.py
   ```

## 💡 Funcionalidades Principales

### 📊 Dashboard
- Visualización de gastos mensuales
- Gráficos por categoría
- Tendencias de gastos
- Estadísticas clave

### 💳 Gestión de Transacciones
- Registro manual de gastos
- Sincronización automática con BCP
- Categorización de gastos
- Historial detallado

### 📧 Integración con Correos
- Conexión segura con Gmail
- Parseo automático de notificaciones BCP
- Actualización en tiempo real

### 👤 Gestión de Usuario
- Registro seguro
- Autenticación robusta
- Gestión de perfil
- Preferencias personalizadas

## 🔒 Seguridad

- Encriptación de datos sensibles
- Manejo seguro de contraseñas
- Protección contra inyección SQL
- Sesiones seguras

## 🤝 Contribución

1. Realizar fork del proyecto en Replit
2. Crear rama para nueva característica
3. Enviar pull request con descripción detallada

## 📝 Notas

- La aplicación está optimizada para uso personal
- Se recomienda realizar backups periódicos
- Las notificaciones BCP deben estar activadas
