# Stage 1: Dependencies (Base for Development)
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

# Copy the rest of the application code for development
COPY . .

# Expose the port Next.js runs on in development
EXPOSE 3000

# Stage 2: Builder (for production build)
FROM base AS builder

WORKDIR /app

# The code is already copied in the base stage, so no need to copy again here.
# If you had specific build-time files not needed for dev, you'd copy them here.
# For Next.js, the `npm run build` command will use the already copied source.

RUN npm run build

# Stage 3: Runner (for production)
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV production

# Copy necessary files from the builder stage for standalone output
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]