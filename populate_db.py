import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Product
from app.core.config import settings
from app.core.security import get_password_hash 

DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    print("ERRO: DATABASE_URL não foi carregada. Verifique seu arquivo .env ou app/core/config.py.")
    sys.exit(1)
else:
    print(f"Usando DATABASE_URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def populate_database():
    Base.metadata.create_all(bind=engine)
    print("Tabelas verificadas/criadas.")

    db = SessionLocal()
    try:
        print("Adicionando usuários...")

        password_alice_plain = "alice_super_secret" 
        password_bob_plain = "bob_super_secret"     

        hashed_password_alice_to_db = get_password_hash(password_alice_plain)
        hashed_password_bob_to_db = get_password_hash(password_bob_plain)

        user_alice = db.query(User).filter(User.email == "alice@example.com").first()
        if not user_alice:
            user_alice = User(
                username="alice",
                email="alice@example.com",
                hashed_password=hashed_password_alice_to_db 
            )
            db.add(user_alice)
            db.commit()
            db.refresh(user_alice)
            print(f"Usuário Alice adicionado com ID: {user_alice.id}")
        else:
            print(f"Usuário Alice já existe (ID: {user_alice.id}). Atualizando senha...")
            user_alice.hashed_password = hashed_password_alice_to_db
            db.commit()
            db.refresh(user_alice)


        user_bob = db.query(User).filter(User.email == "bob@example.com").first()
        if not user_bob:
            user_bob = User(
                username="bob",
                email="bob@example.com",
                hashed_password=hashed_password_bob_to_db 
            )
            db.add(user_bob)
            db.commit()
            db.refresh(user_bob)
            print(f"Usuário Bob adicionado com ID: {user_bob.id}")
        else:
            print(f"Usuário Bob já existe (ID: {user_bob.id}). Atualizando senha...")
            user_bob.hashed_password = hashed_password_bob_to_db
            db.commit()
            db.refresh(user_bob)

        # Adicionar Produtos de Exemplo
        print("Adicionando produtos...")
        products_data = [
            {"name": "Camiseta de Algodão", "description": "Camiseta básica de algodão orgânico.", "user": user_alice},
            {"name": "Calça Jeans Slim Fit", "description": "Calça jeans moderna e confortável.", "user": user_alice},
            {"name": "Tênis Esportivo", "description": "Tênis leve e respirável para corrida.", "user": user_bob},
            {"name": "Smartwatch Avançado", "description": "Monitora saúde e fitness.", "user": user_bob},
            {"name": "Livro de Ficção Científica", "description": "Um best-seller sobre viagens no tempo.", "user": user_alice},
            {"name": "Fone de Ouvido Bluetooth", "description": "Áudio de alta qualidade sem fios.", "user": user_bob},
        ]

        for p_data in products_data:
            if not db.query(Product).filter(Product.name == p_data["name"]).first():
                product = Product(
                    name=p_data["name"],
                    description=p_data["description"],
                    user_id=p_data["user"].id
                )
                db.add(product)
                print(f"Produto '{p_data['name']}' adicionado.")
            else:
                print(f"Produto '{p_data['name']}' já existe.")

        db.commit()
        print("Banco de dados populado com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"Erro ao popular o banco de dados: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()