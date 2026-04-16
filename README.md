# 栖物志 Item Habitat

栖物志是一个面向大学生的 AI 轻量化物品管理系统，目标是给每件物品一个清晰、可追踪、可检索的栖息地。

## 技术栈

- 后端：FastAPI + SQLite
- 前端：Vue 3 + Vite + Pinia + Vue Router
- 测试：`tests/test_receipt_imports.py`

## 目录说明

- `backend/`：FastAPI 后端与数据库访问
- `frontend/`：Vue 3 前端应用
- `uploads/receipt-imports/`：收据导入图片存放目录
- `static/`、`templates/`：历史实现，当前新功能优先使用 `frontend/`

## 启动方式

后端：

```powershell
uv run backend/main.py
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

## 说明

- 前端通过 `/api` 请求后端，开发环境下由 Vite 代理到 `http://127.0.0.1:8000`
- 后端会自动创建数据库和上传目录
- 现有 SQLite 数据库 `warehouse.db` 是历史数据源，修改前请注意兼容性
