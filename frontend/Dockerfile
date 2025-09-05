# Use a Node.js 20 image as the base for building
FROM node:20-alpine AS base

# Set the working directory inside the container
WORKDIR /app

# Install dependencies. Use `npm ci` for clean installs in CI/CD environments.
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then pnpm i --frozen-lockfile; \
  else echo "No lockfile found, installing dependencies with npm install" && npm install; \
  fi

# --- Development Stage ---
FROM node:20-alpine AS dev
WORKDIR /app
COPY --from=base /app/node_modules ./node_modules
# No COPY . . here, as we'll use a volume mount for source code in docker-compose.yml
ENV NEXT_TELEMETRY_DISABLED 1

# Rebuild the source code only when needed
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=base /app/node_modules ./node_modules
COPY . .

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line to disable telemetry.
ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

# Uncomment the following line to disable telemetry.
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]