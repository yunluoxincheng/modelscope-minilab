# ModelScope MiniLab / 智模工坊 后端镜像（CPU 推理，多阶段，多架构）
# 在 GitHub Actions 上用 buildx + QEMU 构建 linux/amd64 + linux/arm64。
# Stage 1 装依赖（含 build-essential），Stage 2 只复制 site-packages，不含编译工具。

# ============ Stage 1: builder ============
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# torch CPU 版：
#   amd64 -> pytorch 官方 CPU index（体积远小于默认 CUDA 版）
#   arm64 -> pypi 默认（arm64 平台 pypi 的 torch 本身就是 CPU 版，无 CUDA 依赖）
ARG TARGETARCH
RUN --mount=type=cache,target=/root/.cache/pip \
    if [ "$TARGETARCH" = "amd64" ]; then \
        pip install --prefix=/install \
            --index-url https://download.pytorch.org/whl/cpu \
            --extra-index-url https://pypi.org/simple \
            torch torchvision; \
    else \
        pip install --prefix=/install torch torchvision; \
    fi

COPY requirements.txt /tmp/requirements.txt
RUN grep -v -iE '^(torch|torchvision)' /tmp/requirements.txt > /tmp/req-no-torch.txt \
    && pip install --prefix=/install -r /tmp/req-no-torch.txt

# ============ Stage 2: runtime ============
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

# 只装运行时系统库：libgl1/libglib2.0-0 给 Pillow；curl 给 healthcheck。
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 把 builder 的 site-packages 与 bin 拷到 /usr/local
COPY --from=builder /install /usr/local

WORKDIR /app
COPY app/ ./app/
COPY ml_assets/ ./ml_assets/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
