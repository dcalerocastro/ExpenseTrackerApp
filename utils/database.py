import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Obtener la URL de la base de datos del entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la base para los modelos
Base = declarative_base()

# Definir los modelos
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=False)
    monto = Column(Float, nullable=False)
    descripcion = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # 'real' o 'proyectado'

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, unique=True, nullable=False)

# Crear las tablas
def init_db():
    Base.metadata.create_all(bind=engine)

# Obtener una sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para migrar datos de CSV a SQL
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
                    tipo=str(row['tipo'])
                )
                db.add(transaction)

        db.commit()
        print("Migración completada exitosamente")

    except Exception as e:
        print(f"Error durante la migración: {e}")
        db.rollback()
    finally:
        db.close()
