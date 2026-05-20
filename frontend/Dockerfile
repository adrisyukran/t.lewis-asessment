# frontend/Dockerfile

FROM node:20-alpine AS builder

WORKDIR /app

# Copy source files
COPY frontend/ ./

# Build step (if needed for minification)
# No build step needed for pure static HTML/JS/CSS

FROM nginx:alpine

# Copy custom nginx configuration
COPY --chown=nginx:nginx frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Cache-bust argument to force rebuild on every build
ARG CACHE_BUST=1

# Copy static files
COPY --chown=nginx:nginx frontend/ /usr/share/nginx/html/

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
