import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, MetaData, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Obtener la URL de la base de datos del entorno
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Inicializando base de datos con URL: {DATABASE_URL}")

# Crear el motor de la base de datos con echo=True para ver las consultas SQL
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la base para los modelos
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    email_accounts = relationship("EmailAccount", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")

class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)
    bank_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_sync = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="email_accounts")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=False)
    monto = Column(Float, nullable=False)
    descripcion = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    moneda = Column(String, nullable=False, default='PEN')
    banco = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="transactions")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, nullable=False)
    notas = Column(Text, nullable=True)
    presupuesto = Column(Float, nullable=True)
    presupuestos = relationship("BudgetHistory", back_populates="category")
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="categories")

class BudgetHistory(Base):
    __tablename__ = "budget_history"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    fecha = Column(DateTime, nullable=False)
    monto = Column(Float, nullable=False)
    category = relationship("Category", back_populates="presupuestos")

def init_db():
    """Initialize the database by creating all tables"""
    try:
        print("\n=== Inicializando Base de Datos ===")

        # Intentar crear las tablas sin eliminar las existentes primero
        print("Creando tablas si no existen...")
        Base.metadata.create_all(bind=engine)

        # Verificar las tablas creadas
        inspector = MetaData()
        inspector.reflect(bind=engine)
        print("\nTablas en la base de datos:")
        for table in inspector.tables:
            print(f"- {table}")

        return True
    except Exception as e:
        print(f"\nError crítico al inicializar la base de datos: {str(e)}")
        return False

# Obtener una sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para migrar datos de CSV a SQL (needs adjustment for BudgetHistory)
def migrate_csv_to_sql():
    """
    Migra los datos existentes de los archivos CSV a la base de datos SQL.
    """
    import pandas as pd
    from pathlib import Path

    # Crear las tablas si no existen
    init_db()
    db = SessionLocal()

    try:
        # Migrar categorías
        csv_path = Path("data/categories.csv")
        if csv_path.exists():
            categories_df = pd.read_csv(csv_path)
            for _, row in categories_df.iterrows():
                category = Category(categoria=row['categoria'])
                db.merge(category)

        # Migrar transacciones
        csv_path = Path("data/transactions.csv")
        if csv_path.exists():
            transactions_df = pd.read_csv(csv_path)
            for _, row in transactions_df.iterrows():
                transaction = Transaction(
                    fecha=pd.to_datetime(row['fecha']),
                    monto=float(row['monto']),
                    descripcion=str(row['descripcion']),
                    categoria=str(row['categoria']),
                    tipo=str(row['tipo']),
                    moneda = str(row.get('moneda', 'PEN')), # Handle missing moneda column
                    banco = str(row.get('banco', None)) # Handle missing banco column

                )
                db.add(transaction)

        # Add Budget History Migration (requires a budget_history.csv file)
        csv_path = Path("data/budget_history.csv")
        if csv_path.exists():
            budget_history_df = pd.read_csv(csv_path)
            for _, row in budget_history_df.iterrows():
                try:
                  budget_entry = BudgetHistory(
                      category_id = int(row['category_id']),
                      fecha = pd.to_datetime(row['fecha']),
                      monto = float(row['monto'])
                  )
                  db.add(budget_entry)
                except (KeyError, ValueError) as e:
                    print(f"Error processing row in budget_history.csv: {row}, Error: {e}")


        db.commit()
        print("Migración completada exitosamente")

    except Exception as e:
        print(f"Error durante la migración: {e}")
        db.rollback()
    finally:
        db.close()