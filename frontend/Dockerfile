# syntax=docker.io/docker/dockerfile:1

############################
# Base image
############################
FROM node:24-alpine AS base

# Protect environment from malware
# Disable writing to /tmp outside app
RUN chmod 1777 /tmp


############################
# Dependencies layer
############################
FROM base AS deps

WORKDIR /app

# Needed for some Node native modules
RUN apk add --no-cache libc6-compat

# Copy manifest files only (proper cache)
COPY package.json package-lock.json* yarn.lock* pnpm-lock.yaml* .npmrc* ./


# Install dependencies based on the available lockfile
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm install --legacy-peer-deps; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm install --frozen-lockfile; \
  else echo "ERROR: Lockfile not found!" && exit 1; \
  fi


############################
# Build layer
############################
FROM base AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1

RUN \
  if [ -f yarn.lock ]; then yarn build; \
  elif [ -f package-lock.json ]; then npm run build; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm run build; \
  else echo "ERROR: Lockfile not found!" && exit 1; \
  fi


############################
# Runtime layer
############################
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Security: restrict system user
RUN addgroup --system --gid 1001 nodejs \
 && adduser --system --uid 1001 nextjs

# Copy production files
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
