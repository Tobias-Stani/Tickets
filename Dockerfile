# --- Stage 1: build Tailwind CSS with the standalone CLI (no Node needed) ---
FROM debian:bookworm-slim AS css
ARG TAILWIND_VERSION=v4.1.13
ADD https://github.com/tailwindlabs/tailwindcss/releases/download/${TAILWIND_VERSION}/tailwindcss-linux-x64 /usr/local/bin/tailwindcss
RUN chmod +x /usr/local/bin/tailwindcss
WORKDIR /build
COPY app/styles app/styles
COPY app/templates app/templates
RUN tailwindcss -i app/styles/input.css -o app/static/css/app.css --minify

# --- Stage 2: runtime ---
FROM python:3.14-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /srv

COPY pyproject.toml ./
RUN mkdir app && touch app/__init__.py && pip install . && rm -rf app

COPY alembic.ini ./
COPY migrations migrations
COPY scripts scripts
COPY app app
COPY --from=css /build/app/static/css/app.css app/static/css/app.css

RUN useradd --create-home appuser && chmod +x scripts/*.sh
USER appuser

EXPOSE 8000
CMD ["scripts/start.sh"]
