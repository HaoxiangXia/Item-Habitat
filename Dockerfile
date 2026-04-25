FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 先复制依赖元数据，提升镜像缓存命中率
COPY pyproject.toml README.md ./

RUN pip install --upgrade pip && pip install .

COPY backend ./backend

# 为 SQLite 与上传文件准备可持久化目录
RUN mkdir -p /data /uploads

ENV WAREHOUSE_DB_PATH=/data/warehouse.db \
    WAREHOUSE_UPLOAD_DIR=/uploads

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]