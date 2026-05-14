# 栖物志 Item Habitat

栖物志是一个面向大学生的 AI 轻量化物品管理系统，目标是给每件物品一个清晰、可追踪、可检索的栖息地。

核心概念：**物品（Items）** 归属于 **空间（Spaces）**，通过 **看板（Board）** 管理状态流转，搭配 **购物截图导入（Receipt Import）** 与 **操作日志（Logs）** 实现全链路追踪。

## 技术栈

- 后端：FastAPI + SQLite
- 前端：Vue 3 + Vite + Pinia + Vue Router

## 目录说明

- `backend/`：FastAPI 后端，包含 `main.py`（路由）、`db.py`（数据库访问）、`schema.sql`（数据表定义）
- `frontend/`：Vue 3 前端应用
- `run_migration.py`：从旧版数据库（products/transactions/storage_locations）向新版模型（items/spaces/categories/logs）的迁移脚本
- `uploads/receipt-imports/`：购物截图上传存放目录
- `docs/`：容器化部署与 PRD 文档

## 核心功能

| 功能 | 说明 |
|------|------|
| **物品管理** | 物品的增删改查、标签、截止时间、状态（pending/stored/taken/archived） |
| **空间地图** | 储物空间以网格卡片展示，支持实景照片与提示语 |
| **状态看板** | 两列看板（待整理/已归位），支持拖拽切换状态 |
| **操作日志** | 所有出入库、移动、状态变更操作自动记录 |
| **购物截图导入** | 上传截图，后端调用 LM Studio 多模态模型做 OCR 识别，自动提取商品信息 |
| **库存统计** | 按空间维度统计物品数量与分布 |
| **登录认证** | 基于简单认证，保护个人数据 |

## 启动方式

### 容器化一键部署（推荐）

项目已支持 Docker Compose 一键启动前后端：

```bash
docker compose up -d
```

启动后访问：`http://localhost:8080`

详细的容器化与服务器部署说明请参考：
- [Docker Compose 部署指南](docs/docker-compose.md)
- [前端容器化说明](docs/docker-frontend.md)
- [后端容器化说明](docs/docker-backend.md)

### 本地开发启动

后端：

```powershell
uv run python -m backend.main
```

前端：

```powershell
cd frontend
npm install
npm run dev
```

## 构建与测试

前端构建：

```powershell
cd frontend
npm run build
```

## 数据库迁移

如果从旧版本升级（旧表：`products`、`transactions`、`storage_locations`），需运行迁移脚本将数据平滑迁移至新版模型：

```powershell
uv run python run_migration.py
```

## 说明

- 前端通过 `/api` 请求后端，开发环境下由 Vite 代理到 `http://127.0.0.1:8000`
- 后端首次启动时自动创建数据库和上传目录
- 默认登录账号：`admin` / `admin`

## LM Studio 接入

如果你本地已经用 LM Studio 跑起了多模态模型，上传购物截图后，后端会自动调用它做 OCR 和商品关键词提取。

可用环境变量：

- `LM_STUDIO_BASE_URL`：LM Studio 的 OpenAI 兼容接口地址，默认 `http://127.0.0.1:1234/v1`
- `LM_STUDIO_MODEL`：模型名称；如果不填，后端会尝试从 `/v1/models` 自动读取
- `LM_STUDIO_API_KEY`：如果你在 LM Studio 里启用了密钥校验，可以填这里
- `LM_STUDIO_TIMEOUT`：模型请求超时时间，默认 `60`

如果本地模型暂时不可用，系统会自动降级成可编辑的手动草稿，不会阻断上传流程。

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `WAREHOUSE_DB_PATH` | 数据库文件路径 | `warehouse.db` |
| `WAREHOUSE_UPLOAD_DIR` | 上传文件根目录 | `uploads/` |
