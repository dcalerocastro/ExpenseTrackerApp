
# Control de Gastos - Aplicación de Gestión Financiera Personal

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

## Buenas Prácticas Implementadas

### Seguridad
- Almacenamiento seguro de contraseñas con hash
- Variables de entorno para credenciales
- Autenticación requerida para acceso
- SSL/TLS para conexiones a base de datos

### Base de Datos
- Uso de ORM (SQLAlchemy) para abstracción
- Migraciones automáticas de esquema
- Transacciones atómicas para operaciones críticas
- Control de conexiones con sessionmaker

### Código
- Separación clara de responsabilidades (módulos)
- Manejo de errores consistente
- Logging para debugging
- Tipado de datos en modelos
- Comentarios descriptivos en funciones clave

### UI/UX
- Interfaz responsive y moderna
- Feedback inmediato al usuario
- Validación de formularios
- Mensajes de error claros
- Navegación intuitiva

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

## Mantenimiento

- Realizar backups regulares de la base de datos
- Monitorear logs de errores
- Actualizar dependencias periódicamente
- Revisar conexiones de correo y base de datos

## Contribución

1. Mantener el estilo de código consistente
2. Documentar cambios significativos
3. Añadir tests para nuevas funcionalidades
4. Seguir el flujo de trabajo git establecido

## Soporte

Para reportar problemas o sugerir mejoras, usar el sistema de issues del repositorio.
