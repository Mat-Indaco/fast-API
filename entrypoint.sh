#!/bin/bash
set -e

echo "⏳ Corriendo migraciones Alembic..."
uv run alembic upgrade head

echo "🌱 Seedeando usuarios de prueba..."
uv run python seed.py

echo "🚀 Iniciando servidor..."
exec uv run uvicorn main:app --host 0.0.0.0 --port 8000