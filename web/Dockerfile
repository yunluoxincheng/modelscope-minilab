# ModelScope MiniLab / 智模工坊 Web 前端镜像
# 多阶段：Stage 1 Node 构建静态资源，Stage 2 nginx 托管并反代 /api 到 backend。
# 在 GitHub Actions 上用 buildx + QEMU 构建 linux/amd64 + linux/arm64。

# ============ Stage 1: builder ============
FROM node:20-alpine AS builder

WORKDIR /build

# 先拷依赖清单再装依赖，充分利用 Docker 层缓存
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund

COPY . .
RUN npm run build

# ============ Stage 2: runtime ============
FROM nginx:1.27-alpine

ENV TZ=Asia/Shanghai

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /build/dist /usr/share/nginx/html

EXPOSE 80

# nginx:alpine 自带 busybox wget，足够做存活探测
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q --spider http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
