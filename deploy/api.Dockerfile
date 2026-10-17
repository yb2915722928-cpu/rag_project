ARG PYTHON_BASE_IMAGE
ARG UV_BASE_IMAGE
FROM ${UV_BASE_IMAGE} AS uv
FROM ${PYTHON_BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH=/opt/venv/bin:$PATH

WORKDIR /app
COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock .python-version ./

RUN python -c "import sys; assert sys.implementation.name == 'cpython' and sys.version_info[:3] == (3,12,8)" \
    && uv sync --locked --no-dev --no-install-project --python /usr/local/bin/python \
    && /opt/venv/bin/python -c "from importlib.metadata import version; assert version('uvicorn') == '0.37.0'"

COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./
COPY --from=worker_health healthcheck.py /usr/local/bin/rag-worker-healthcheck

RUN /opt/venv/bin/python -c "import rag_app, rag_app.entrypoints.api, rag_app.entrypoints.worker" \
    && ! find /app -xdev -perm /022 -print -quit | grep -q .

USER 65532:65532
