FROM node:22-alpine AS web-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN corepack enable && corepack prepare pnpm@9.15.9 --activate && pnpm install --frozen-lockfile
COPY frontend/ ./
ENV VITE_ADMIN_ROUTE_PREFIX=/admin
RUN pnpm build

FROM nginx:1.28-alpine AS web
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=web-build /app/frontend/dist /usr/share/nginx/html

FROM python:3.11-slim AS api
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home app && mkdir /data && chown app:app /data /app
COPY --chown=app:app backend/ ./backend/
USER app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--no-proxy-headers"]
