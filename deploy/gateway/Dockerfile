ARG NGINX_BASE_IMAGE
FROM ${NGINX_BASE_IMAGE}
COPY deploy/gateway/nginx.conf /etc/nginx/nginx.conf
COPY frontend/dist/ /usr/share/nginx/html/
RUN test -s /usr/share/nginx/html/index.html
USER 65532:65532
