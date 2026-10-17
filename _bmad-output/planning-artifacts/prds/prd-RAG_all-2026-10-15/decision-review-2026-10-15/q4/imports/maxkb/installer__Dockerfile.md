# MaxKB source excerpt: installer/Dockerfile

- source: https://github.com/1Panel-dev/MaxKB/blob/0fa9a0dae8850c1878f087f0d81c974c1d424b06/installer/Dockerfile
- raw: https://raw.githubusercontent.com/1Panel-dev/MaxKB/0fa9a0dae8850c1878f087f0d81c974c1d424b06/installer/Dockerfile
- publisher: 1Panel-dev/MaxKB
- pub_date: 未标
- accessed: 2026-10-15
- confidence: medium（单一官方源）
- class: official-pinned-source

```text
1: FROM node:24-alpine AS web-build
2: COPY ui ui
3: RUN cd ui && ls -la && if [ -d "dist" ]; then exit 0; fi && \
4:     npm install --prefer-offline --no-audit && \
5:     npm install -D concurrently && \
6:     NODE_OPTIONS="--max-old-space-size=4096" npx concurrently "npm run build" "npm run build-chat" && \
7:     find . -maxdepth 1 ! -name '.' ! -name 'dist' ! -name 'public' -exec rm -rf {} +
...
27: FROM ghcr.io/1panel-dev/maxkb-base:python3.11-pg17.11-20260903
28: ARG DOCKER_IMAGE_TAG=dev \
29:     BUILD_AT \
30:     GITHUB_COMMIT
31: 
32: ENV MAXKB_VERSION="${DOCKER_IMAGE_TAG} (build at ${BUILD_AT}, commit: ${GITHUB_COMMIT})" \
33:     MAXKB_DB_NAME=maxkb \
34:     MAXKB_DB_HOST=127.0.0.1 \
35:     MAXKB_DB_PORT=5432  \
36:     MAXKB_DB_USER=${POSTGRES_USER} \
37:     MAXKB_DB_PASSWORD=${POSTGRES_PASSWORD} \
38:     MAXKB_DB_MAX_OVERFLOW=80 \
39:     MAXKB_REDIS_HOST=127.0.0.1 \
40:     MAXKB_REDIS_PORT=6379 \
41:     MAXKB_REDIS_DB=0 \
42:     MAXKB_REDIS_PASSWORD=${REDIS_PASSWORD} \
...
54: EXPOSE 8080
55: VOLUME /opt/maxkb
56: ENTRYPOINT ["bash", "-c"]
57: CMD [ "/usr/bin/start-all.sh" ]
```
