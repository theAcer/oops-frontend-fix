# Stage 1: Dependencies
FROM node:20-alpine AS base

WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package.json package-lock.json* ./

# Install dependencies
# Use npm ci for clean install if package-lock.json exists, otherwise npm install
RUN \
  if [ -f package-lock.json ]; then npm ci; \
  else npm install; \
  fi

# Stage 2: Builder (for production build, not used in dev profile but good practice)
FROM base AS builder

WORKDIR /app

COPY . .

RUN npm run build

# Stage 3: Runner (for production, not used in dev profile but good practice)
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]