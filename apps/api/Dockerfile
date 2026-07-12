FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY pyproject.toml README.md ./
COPY apps/api/src ./apps/api/src
COPY packages/shared-types/src ./packages/shared-types/src

RUN pip install --upgrade pip && pip install .

EXPOSE 8080

CMD ["uvicorn", "devos_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
