# Docker 部署前端服务

本文档说明如何单独构建并运行前端容器。

## 前提条件

- 已安装 Docker
- 后端服务可访问（推荐使用同一套 compose 网络）

## 1. 构建前端镜像

在项目根目录执行：

```bash
docker build -t item-habitat-frontend:latest ./frontend
```

## 2. 运行前端容器

```bash
docker run -d \
  --name item-habitat-frontend \
  -p 8080:80 \
  --restart unless-stopped \
  item-habitat-frontend:latest
```

## 3. 访问前端

```text
http://127.0.0.1:8080
```

## 4. API 连接说明

前端容器使用 Nginx 转发：

- `/api/*` -> `http://backend:8000/api/*`
- `/uploads/*` -> `http://backend:8000/uploads/*`

如果你不是用 `docker compose` 启动，而是单独 `docker run` 前端容器：

- 需要保证容器网络中存在名为 `backend` 的后端服务
- 或自行修改 `frontend/nginx.conf` 中的上游地址并重新构建镜像
