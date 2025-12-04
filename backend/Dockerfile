FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

COPY src/ ./src/
COPY alembic.ini ./
COPY alembic/ ./alembic/

EXPOSE 8787

CMD ["uvicorn", "agent_platform.main:app", "--host", "0.0.0.0", "--port", "8787"]

