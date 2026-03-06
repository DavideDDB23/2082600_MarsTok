# =============================================================================
# frontend/Dockerfile  (multi-stage)
# Build context: source/   (set in docker-compose.yml)
# =============================================================================

# ── Stage 1: Build React/Vite app ─────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install deps first for layer caching
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

# Copy source and build
COPY frontend/ .
RUN npm run build

# ── Stage 2: Serve with nginx ─────────────────────────────────────────────
FROM nginx:stable-alpine

# Custom nginx config (SPA fallback + API proxy)
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy Vite build output
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
