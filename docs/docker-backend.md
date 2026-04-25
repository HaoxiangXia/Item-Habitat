# Docker 部署后端服务

本文档说明如何使用 Docker 单独构建并运行后端服务。

## 前提条件

- 已安装 Docker（建议 24+）
- 当前目录位于项目根目录

## 1. 构建镜像

```bash
docker build -t item-habitat-backend:latest .
```

## 2. 运行容器

```bash
docker run -d \
  --name item-habitat-backend \
  -p 8000:8000 \
  -e WAREHOUSE_DB_PATH=/data/warehouse.db \
  -e WAREHOUSE_UPLOAD_DIR=/uploads \
  -v item_habitat_data:/data \
  -v item_habitat_uploads:/uploads \
  --restart unless-stopped \
  item-habitat-backend:latest
```

## 3. 验证服务

```bash
curl http://127.0.0.1:8000/api/products
```

如果返回 JSON（可能是空数组）说明服务可用。

## 4. 常用运维命令

查看日志：

```bash
docker logs -f item-habitat-backend
```

停止容器：

```bash
docker stop item-habitat-backend
```

删除容器：

```bash
docker rm item-habitat-backend
```

## 5. LM Studio（可选）

如需开启收据图片识别，可在 `docker run` 中增加环境变量：

```bash
-e LM_STUDIO_BASE_URL=http://host.docker.internal:1234/v1 \
-e LM_STUDIO_MODEL=unsloth/gemma-4-e4b-it \
-e LM_STUDIO_API_KEY= \
-e LM_STUDIO_TIMEOUT=60
```

说明：

- Linux 环境下，如果 `host.docker.internal` 不可用，请改成宿主机实际 IP
- 生产环境建议通过反向代理或密钥管理传递 API 密钥
