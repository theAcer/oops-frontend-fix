# Install dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json ./
RUN rm -f package-lock.json && npm install

# Builder stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Runner stage
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
# Uncomment the following line in case you want to disable telemetry during runtime.
# ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy the entire standalone output, which includes .next/static and public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./


USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]