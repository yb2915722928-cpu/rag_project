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

# The Gitee checkout can carry an operator umask such as 077, and COPY
# preserves those host modes. Normalize only the image content owned by this
# build so the service UID can read/traverse it, without granting group or
# other write access. Secret exclusions remain governed by the Dockerignore.
RUN chown -R 0:0 /app \
    && chmod -R u+rwX,go+rX /app

RUN /opt/venv/bin/python -c "import rag_app, rag_app.entrypoints.api, rag_app.entrypoints.worker" \
    && ! find /app -xdev -perm /022 -print -quit | grep -q .

USER 65532:65532

# The final check runs as the actual service UID. It proves the package,
# configuration and migrations are readable after the mode normalization;
# root-only build-time imports did not catch the earlier 0700/0600 failure.
RUN /opt/venv/bin/python -c "from pathlib import Path; files = ['/app/pyproject.toml', '/app/uv.lock', '/app/alembic.ini', '/app/migrations/env.py', '/app/migrations/versions/0002_isolated_calls.py']; [open(path, 'rb').read(1) for path in files]; import rag_app, rag_app.adapters.epoch_control, rag_app.adapters.postgres, rag_app.bootstrap.runtime, rag_app.entrypoints.api, rag_app.entrypoints.worker; print('SERVICE_UID_IMPORT_OK')"
