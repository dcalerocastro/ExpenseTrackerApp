from datetime import datetime
import traceback
from .database import SessionLocal, Transaction, Category, BudgetHistory, init_db
import pandas as pd

def ensure_data_exists(user_id: int = None):
    """Asegura que la base de datos está inicializada con las categorías por defecto para un usuario"""
    print("\n--- Verificando base de datos ---")
    db = SessionLocal()
    try:
        # Inicializar la base de datos si no existe
        init_db()

        if user_id is not None:
            # Verificar si hay categorías para el usuario
            if db.query(Category).filter(Category.user_id == user_id).count() == 0:
                print(f"Inicializando categorías por defecto para usuario {user_id}")
                default_categories = [
                    ("Gastos Corrientes", "Gastos regulares y frecuentes como suscripciones", 100.0),
                    ("Casa", "Gastos relacionados con el hogar, mantenimiento y mejoras", 200.0),
                    ("Servicios Básicos", "Luz, agua, gas, internet, teléfono", 300.0),
                    ("Transporte", "Gasolina, transporte público, mantenimiento de vehículos", 150.0),
                    ("Alimentación", "Comida, restaurantes, delivery", 500.0),
                    ("Salud", "Medicamentos, consultas médicas, seguros de salud", 200.0),
                    ("Entretenimiento", "Cine, streaming, salidas, hobbies", 100.0),
                    ("Sin Categorizar", "Gastos pendientes de categorizar", 0.0)
                ]
                for cat, nota, presup in default_categories:
                    nueva_categoria = Category(
                        categoria=cat, 
                        presupuesto=presup,
                        notas=nota,
                        user_id=user_id
                    )
                    db.add(nueva_categoria)
                    db.flush()  # Para obtener el ID

                    # Agregar primer registro histórico
                    hist = BudgetHistory(
                        category_id=nueva_categoria.id,
                        fecha=datetime.now(),
                        monto=presup
                    )
                    db.add(hist)
                db.commit()
                print("Categorías por defecto creadas")
    except Exception as e:
        print(f"Error verificando datos: {str(e)}")
        db.rollback()
    finally:
        db.close()

def load_categories_with_budget(fecha: datetime = None, user_id: int = None):
    """Carga todas las categorías con sus presupuestos y notas para una fecha específica y usuario"""
    ensure_data_exists(user_id)
    if fecha is None:
        fecha = datetime.now()

    print(f"\n=== Cargando categorías con presupuestos para {fecha} ===")
    db = SessionLocal()
    try:
        categories_with_budget = []
        query = db.query(Category)
        if user_id is not None:
            query = query.filter(Category.user_id == user_id)
        categories = query.all()
        print(f"Encontradas {len(categories)} categorías")

        for cat in categories:
            # Obtener el presupuesto más reciente antes o igual a la fecha dada
            hist = db.query(BudgetHistory)\
                    .filter(
                        BudgetHistory.category_id == cat.id,
                        BudgetHistory.fecha <= fecha
                    )\
                    .order_by(BudgetHistory.fecha.desc(), BudgetHistory.id.desc())\
                    .first()

            budget = hist.monto if hist else cat.presupuesto
            categories_with_budget.append((cat.categoria, budget, cat.notas))

        return categories_with_budget
    except Exception as e:
        print(f"Error cargando categorías: {str(e)}")
        print(traceback.format_exc())
        return []
    finally:
        db.close()

def load_categories(user_id: int = None):
    """Carga todas las categorías de un usuario específico"""
    ensure_data_exists(user_id)
    db = SessionLocal()
    try:
        query = db.query(Category)
        if user_id is not None:
            query = query.filter(Category.user_id == user_id)
        categories = query.all()
        return [cat.categoria for cat in categories]
    except Exception as e:
        print(f"Error cargando categorías: {str(e)}")
        return ["Sin Categorizar"]
    finally:
        db.close()

def save_categories(categories, user_id: int = None):
    """Guarda las categorías para un usuario específico"""
    db = SessionLocal()
    try:
        # Obtener las categorías existentes con sus presupuestos y notas
        query = db.query(Category)
        if user_id is not None:
            query = query.filter(Category.user_id == user_id)
        existing_categories = {cat.categoria: (cat.presupuesto, cat.notas) 
                             for cat in query.all()}

        # Eliminar categorías existentes del usuario
        if user_id is not None:
            db.query(Category).filter(Category.user_id == user_id).delete()
        else:
            db.query(Category).delete()

        # Agregar nuevas categorías manteniendo los presupuestos y notas existentes
        for cat in categories:
            presupuesto, notas = existing_categories.get(cat, (0.0, ""))
            db.add(Category(
                categoria=cat,
                presupuesto=presupuesto,
                notas=notas,
                user_id=user_id
            ))

        db.commit()
        return True
    except Exception as e:
        print(f"Error guardando categorías: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def save_transaction(transaction_data, user_id: int = None):
    """Guarda una nueva transacción para un usuario específico"""
    print("\n=== INICIANDO GUARDADO DE TRANSACCIÓN ===")
    print(f"Datos recibidos: {transaction_data}")

    required_fields = ['fecha', 'monto', 'descripcion', 'categoria']
    for field in required_fields:
        if field not in transaction_data:
            print(f"Error: Campo requerido faltante: {field}")
            return False

    db = SessionLocal()
    try:
        if isinstance(transaction_data['fecha'], str):
            transaction_data['fecha'] = pd.to_datetime(transaction_data['fecha'])

        new_transaction = Transaction(
            fecha=transaction_data['fecha'],
            monto=float(transaction_data['monto']),
            descripcion=str(transaction_data['descripcion']),
            categoria=str(transaction_data['categoria']),
            tipo=str(transaction_data.get('tipo', 'real')),
            moneda=str(transaction_data.get('moneda', 'PEN')),
            user_id=user_id
        )

        db.add(new_transaction)
        db.commit()
        print("Transacción guardada exitosamente")
        return True

    except Exception as e:
        print(f"Error guardando transacción: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        return False
    finally:
        db.close()

def load_transactions(user_id: int = None):
    """Carga todas las transacciones de un usuario específico"""
    ensure_data_exists(user_id)
    db = SessionLocal()
    try:
        print("\n--- Cargando transacciones ---")
        query = db.query(Transaction)
        if user_id is not None:
            query = query.filter(Transaction.user_id == user_id)
        transactions = query.all()

        if transactions:
            data = [{
                'fecha': t.fecha,
                'monto': t.monto,
                'descripcion': t.descripcion,
                'categoria': t.categoria,
                'tipo': t.tipo,
                'moneda': t.moneda
            } for t in transactions]
            df = pd.DataFrame(data)
            print(f"Transacciones cargadas: {len(df)} registros")
            return df
        return pd.DataFrame(columns=['fecha', 'monto', 'descripcion', 'categoria', 'tipo', 'moneda'])

    except Exception as e:
        print(f"Error cargando transacciones: {str(e)}")
        print(traceback.format_exc())
        return pd.DataFrame(columns=['fecha', 'monto', 'descripcion', 'categoria', 'tipo', 'moneda'])
    finally:
        db.close()

def update_category_notes(categoria: str, notas: str):
    """Actualiza las notas de una categoría"""
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.categoria == categoria).first()
        if category:
            category.notas = notas
            db.commit()
            return True
        return False
    except Exception as e:
        print(f"Error actualizando notas: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def update_category_budget(categoria: str, presupuesto: float, fecha: datetime = None):
    """Actualiza el presupuesto de una categoría y guarda el histórico"""
    if fecha is None:
        fecha = datetime.now()

    print(f"\n=== Actualizando presupuesto de {categoria} ===")
    print(f"Nuevo presupuesto: {presupuesto}")
    print(f"Fecha: {fecha}")

    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.categoria == categoria).first()
        if category:
            print(f"Categoría encontrada, ID: {category.id}")

            # Actualizar presupuesto actual en la tabla Category
            category.presupuesto = presupuesto

            # Agregar registro histórico
            hist = BudgetHistory(
                category_id=category.id,
                fecha=fecha,
                monto=presupuesto
            )
            db.add(hist)
            db.commit()

            print("Presupuesto actualizado exitosamente")
            print(f"Presupuesto en categoría: {category.presupuesto}")
            return True

        print("Categoría no encontrada")
        return False

    except Exception as e:
        print(f"Error actualizando presupuesto: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        return False
    finally:
        db.close()

def get_budget_history(categoria: str = None):
    """Obtiene el histórico de presupuestos para una o todas las categorías"""
    db = SessionLocal()
    try:
        query = db.query(
            Category.categoria,
            BudgetHistory.fecha,
            BudgetHistory.monto
        ).join(BudgetHistory)

        if categoria:
            query = query.filter(Category.categoria == categoria)

        query = query.order_by(Category.categoria, BudgetHistory.fecha.desc())

        results = query.all()
        return [(r.categoria, r.fecha, r.monto) for r in results]
    except Exception as e:
        print(f"Error obteniendo histórico: {str(e)}")
        return []
    finally:
        db.close()