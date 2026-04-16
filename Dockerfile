# ============================================
# 第一阶段：构建阶段
# ============================================
FROM python:3.11-alpine AS builder

# 安装构建依赖
RUN apk add --no-cache gcc musl-dev

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖到独立目录
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# 第二阶段：运行阶段
# ============================================
FROM python:3.11-alpine

# 安装运行时依赖（仅保留必要的）
RUN apk add --no-cache libffi libstdc++

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

# 创建非 root 用户
RUN addgroup -g 1000 -S appgroup && \
    adduser -u 1000 -S appuser -G appgroup

# 设置工作目录
WORKDIR /app

# 从构建阶段复制已安装的依赖
COPY --from=builder /install /usr/local

# 复制项目代码
COPY --chown=appuser:appgroup . .

# 创建数据目录并设置权限
RUN mkdir -p /app/data && chown -R appuser:appgroup /app

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 5000

# 启动指令
ENTRYPOINT ["python", "app.py", "--host", "0.0.0.0"]