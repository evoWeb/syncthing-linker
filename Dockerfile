# Stage 1: Builder
FROM node:20-alpine AS builder

WORKDIR /build
COPY app/package*.json ./
COPY app/tsconfig.json ./
RUN npm install
COPY app/src ./src
RUN npm run build

# Stage 2: Final Image
FROM node:20-alpine

WORKDIR /usr/src/app

COPY app/package*.json ./
RUN npm install --production

COPY --from=builder /build/dist ./dist
COPY config /config

CMD [ "node", "dist/main.js" ]
