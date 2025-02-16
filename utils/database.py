import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, MetaData, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Obtener la URL de la base de datos del entorno
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Inicializando base de datos con URL: {DATABASE_URL}")

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la base para los modelos
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    app_password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=False)
    monto = Column(Float, nullable=False)
    descripcion = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # 'real' o 'proyectado'
    moneda = Column(String, nullable=False, default='PEN')
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", backref="transactions")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, nullable=False)
    notas = Column(Text, nullable=True)
    presupuesto = Column(Float, nullable=True)
    presupuestos = relationship("BudgetHistory", back_populates="category")
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", backref="categories")

class BudgetHistory(Base):
    __tablename__ = "budget_history"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    fecha = Column(DateTime, nullable=False)
    monto = Column(Float, nullable=False)
    category = relationship("Category", back_populates="presupuestos")

# Crear las tablas
def init_db():
    try:
        print("Iniciando creación de tablas...")
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas exitosamente")

        # Verificar las tablas creadas
        inspector = MetaData()
        inspector.reflect(bind=engine)
        print("Tablas en la base de datos:")
        for table in inspector.tables:
            print(f"- {table}")
    except Exception as e:
        print(f"Error al crear tablas: {str(e)}")
        raise e

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
                    moneda = str(row.get('moneda', 'PEN')) # Handle missing moneda column
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