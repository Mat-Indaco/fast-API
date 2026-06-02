"""Script para poblar la DB con usuarios de prueba."""
from sqlmodel import Session, create_engine, select
from models import User, UserRole
from security import hash_password

DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL)

def seed():
    users = [
        User(
            username="admin",
            email="admin@example.com",
            full_name="Administrador",
            hashed_password=hash_password("admin"),
            role=UserRole.ADMIN,
        ),
        User(
            username="user",
            email="user@example.com",
            full_name="Usuario Normal",
            hashed_password=hash_password("user"),
            role=UserRole.USER,
        ),
        User(
            username="user2",
            email="user2@example.com",
            full_name="Usuario Normal 2",
            hashed_password=hash_password("user2"),
            role=UserRole.USER,
        ),
    ]

    with Session(engine) as session:
        for u in users:
            exists = session.exec(
                select(User).where(User.username == u.username)
            ).first()
            if not exists:
                session.add(u)
        session.commit()
        print("✅ Seed completado.")

if __name__ == "__main__":
    seed()