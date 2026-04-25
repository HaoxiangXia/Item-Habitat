# Docker Compose 镜像部署（服务器）

本文档说明如何在本地构建镜像，然后将镜像上传到局域网服务器并使用 `docker-compose.yml` 部署。

## 前提条件

- 已安装 Docker 与 Docker Compose 插件（`docker compose`）
- 当前目录位于项目根目录

## 1. 启动服务

```bash
docker compose up -d
```

前提：

- 服务器已经通过 `docker load` 导入 `item-habitat-backend:2026.04.26`
- 服务器已经通过 `docker load` 导入 `item-habitat-frontend:2026.04.26`

## 2. 本地构建并导出镜像

在你的 PC 项目根目录执行：

```bash
docker buildx build --platform linux/amd64 -t item-habitat-backend:2026.04.26 --load .
docker buildx build --platform linux/amd64 -t item-habitat-frontend:2026.04.26 --load ./frontend
docker save -o item-habitat-backend_2026.04.26.tar item-habitat-backend:2026.04.26
docker save -o item-habitat-frontend_2026.04.26.tar item-habitat-frontend:2026.04.26
```

## 3. 上传到服务器并导入镜像

上传文件：

```bash
scp item-habitat-backend_2026.04.26.tar <user>@<server-ip>:/opt/Item-Habitat/
scp item-habitat-frontend_2026.04.26.tar <user>@<server-ip>:/opt/Item-Habitat/
scp docker-compose.yml <user>@<server-ip>:/opt/Item-Habitat/
scp warehouse.db <user>@<server-ip>:/opt/Item-Habitat/
rsync -av uploads/ <user>@<server-ip>:/opt/Item-Habitat/uploads/
```

在服务器导入：

```bash
cd /opt/Item-Habitat
docker load -i item-habitat-backend_2026.04.26.tar
docker load -i item-habitat-frontend_2026.04.26.tar
```

## 4. 查看状态与日志

查看服务状态：

```bash
docker compose ps
```

查看后端日志：

```bash
docker compose logs -f backend
```

查看前端日志：

```bash
docker compose logs -f frontend
```

## 3. 访问服务

前端地址：

```text
http://127.0.0.1:8080
```

后端地址（通常由前端反向代理访问）：

```text
http://127.0.0.1:8000
```

示例接口：

```text
GET http://127.0.0.1:8000/api/products
```

## 5. 停止与清理

停止服务：

```bash
docker compose down
```

连同数据卷一起删除（谨慎）：

```bash
docker compose down -v
```

## 6. 服务说明

- `backend`：FastAPI 服务，监听容器内 `8000`
- `frontend`：Nginx 托管 Vue 构建产物，监听容器内 `80`，映射到宿主机 `8080`
- 前端容器内 `/api` 与 `/uploads` 请求会自动反向代理到 `backend:8000`

## 7. 环境变量说明

`docker-compose.yml` 已内置以下变量：

- `WAREHOUSE_DB_PATH=/data/warehouse.db`
- `WAREHOUSE_UPLOAD_DIR=/uploads`

可选 LM Studio 变量已在 compose 文件中注释，如需启用请取消注释并调整地址。

## 8. 数据持久化

compose 使用宿主机绑定挂载：

- `./warehouse.db`：SQLite 数据库文件
- `./uploads/`：上传图片目录

即使容器重建，这些本地文件也会保留。

如果你之前已经把数据写入旧的 Docker 命名卷，可按下面方式迁移：

```bash
docker run --rm \
	-v item-habitat_item_habitat_data:/from \
	-v "$PWD":/to \
	alpine sh -c 'cp /from/warehouse.db /to/warehouse.db'
```

迁移后重启：

```bash
docker compose down
docker compose up -d
```
