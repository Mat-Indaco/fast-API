"""Pobla la DB con usuarios, categorías y tareas de prueba."""

from datetime import date, datetime, timezone

from sqlmodel import Session, create_engine, select

from models import Category, Priority, Task, TaskStatus, User, UserRole
from security import hash_password

DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL)


def seed():
    with Session(engine) as session:
        _seed_users(session)
        _seed_categories(session)
        _seed_tasks(session)
        print("Seed completado.")


def _seed_users(session: Session):
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
    for u in users:
        if not session.exec(select(User).where(User.username == u.username)).first():
            session.add(u)
    session.commit()


def _seed_categories(session: Session):
    user = session.exec(select(User).where(User.username == "user")).first()
    if not user:
        return

    cats = [
        Category(name="Trabajo", color="#6366f1", owner_id=user.id),
        Category(name="Personal", color="#10b981", owner_id=user.id),
        Category(name="Estudio", color="#f59e0b", owner_id=user.id),
    ]
    for c in cats:
        exists = session.exec(
            select(Category).where(
                Category.name == c.name, Category.owner_id == user.id
            )
        ).first()
        if not exists:
            session.add(c)
    session.commit()


def _seed_tasks(session: Session):
    user = session.exec(select(User).where(User.username == "user")).first()
    if not user:
        return

    trabajo = session.exec(
        select(Category).where(
            Category.name == "Trabajo", Category.owner_id == user.id
        )
    ).first()
    personal = session.exec(
        select(Category).where(
            Category.name == "Personal", Category.owner_id == user.id
        )
    ).first()
    estudio = session.exec(
        select(Category).where(
            Category.name == "Estudio", Category.owner_id == user.id
        )
    ).first()

    tasks = [
        Task(
            title="Revisar PRs pendientes",
            description="Hacer code review de las PRs abiertas en el repositorio",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH,
            due_date=date(2026, 6, 28),
            category_id=trabajo.id if trabajo else None,
            owner_id=user.id,
            created_at=datetime.now(timezone.utc),
        ),
        Task(
            title="Escribir tests para el módulo de auth",
            description="Cubrir casos de token expirado y credenciales inválidas",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            due_date=date(2026, 6, 30),
            category_id=trabajo.id if trabajo else None,
            owner_id=user.id,
            created_at=datetime.now(timezone.utc),
        ),
        Task(
            title="Actualizar dependencias del proyecto",
            status=TaskStatus.PENDING,
            priority=Priority.LOW,
            due_date=date(2026, 7, 15),
            category_id=trabajo.id if trabajo else None,
            owner_id=user.id,
            created_at=datetime.now(timezone.utc),
        ),
        Task(
            title="Leer Clean Architecture",
            description="Capítulos 5 al 10",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.MEDIUM,
            due_date=date(2026, 7, 10),
            category_id=estudio.id if estudio else None,
            owner_id=user.id,
            created_at=datetime.now(timezone.utc),
        ),
        Task(
            title="Practicar algoritmos de grafos",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            category_id=estudio.id if estudio else None,
            owner_id=user.id,
            created_at=datetime.now(timezone.utc),
        ),
        Task(
            title="Renovar el gimnasio",
            status=TaskStatus.DONE,
            priority=Priority.LOW,
            category_id=personal.id if personal else None,
            owner_id=user.id,
            created_at=datetime.now(timezone.utc),
        ),
        Task(
            title="Planificar vacaciones",
            description="Buscar opciones para julio",
            status=TaskStatus.PENDING,
            priority=Priority.LOW,
            due_date=date(2026, 6, 20),
            category_id=personal.id if personal else None,
            owner_id=user.id,
            created_at=datetime.now(timezone.utc),
        ),
    ]

    existing_titles = {
        t.title
        for t in session.exec(select(Task).where(Task.owner_id == user.id)).all()
    }
    for t in tasks:
        if t.title not in existing_titles:
            session.add(t)
    session.commit()


if __name__ == "__main__":
    seed()
