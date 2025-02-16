├── utils/
│   ├── auth.py          # Autenticación
│   ├── data_manager.py  # Gestión de datos
│   ├── database.py      # Configuración DB
│   ├── email_parser.py  # Parser de correos
│   ├── email_reader.py  # Lector de correos
│   └── encryption.py    # Seguridad
├── main.py              # App principal
└── test_app_flow.py     # Tests
```

## 🚀 Inicio Rápido

1. **Configuración**
   ```
   DATABASE_URL=postgresql://user:pass@host/db
   EMAIL_ACCOUNT=your-email@gmail.com
   ```

2. **Iniciar App**
   ```bash
   streamlit run main.py