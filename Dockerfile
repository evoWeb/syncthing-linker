# Stage 1: Builder
FROM node:25-alpine AS builder

WORKDIR /build

COPY app/eslint.config.mjs ./
COPY app/package*.json ./
COPY app/tsconfig.json ./
COPY app/src ./src

RUN npm install
RUN npm run build

# Stage 2: Final Image
FROM node:25-alpine

# Install su-exec for privilege dropping
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN apk add --no-cache su-exec
ENTRYPOINT ["/entrypoint.sh"]

WORKDIR /usr/src/app

COPY app/package*.json ./
RUN npm install --production

COPY --from=builder /build/dist ./dist
COPY config /config

HEALTHCHECK \
    --interval=30s \
    --timeout=10s \
    --start-period=5s \
    --retries=3 \
    CMD pgrep -f "node dist/main.js" || exit 1

CMD ["node", "dist/main.js"]
