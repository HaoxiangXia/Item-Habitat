from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, List, Optional
from uuid import uuid4
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from backend import db
except ImportError:  # pragma: no cover - fallback for direct script execution
    import sys

    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from backend import db


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_ROOT = Path(os.getenv("WAREHOUSE_UPLOAD_DIR", str(BASE_DIR / "uploads")))
RECEIPT_IMPORT_DIR = UPLOAD_ROOT / "receipt-imports"
MAX_RECEIPT_IMAGE_SIZE = 5 * 1024 * 1024
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://127.0.0.1:1234/v1").rstrip("/")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "unsloth/gemma-4-e4b-it").strip()
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "").strip()
LM_STUDIO_TIMEOUT = float(os.getenv("LM_STUDIO_TIMEOUT", "60"))
ALLOWED_IMAGE_TYPES = {
    "png": "png",
    "jpeg": "jpg",
    "gif": "gif",
    "webp": "webp",
}


class StorageLocationCreate(BaseModel):
    name: str = Field(min_length=1)


class InboundCreate(BaseModel):
    name: str = Field(min_length=1)
    quantity: int = Field(default=1, ge=1)
    storageLocation: str = ""
    note: str = ""


class OutboundCreate(BaseModel):
    productId: int = Field(ge=1)
    quantity: int = Field(default=1, ge=1)
    note: str = ""


class CheckProductRequest(BaseModel):
    name: str = Field(default="")


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    storageLocation: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class ReceiptImportItemUpdate(BaseModel):
    name: str = Field(default="")
    quantity: int = Field(default=1, ge=1)
    storageLocation: str = Field(default="")
    note: str = Field(default="")


class ReceiptImportDraftUpdate(BaseModel):
    note: str = Field(default="")
    items: List[ReceiptImportItemUpdate] = Field(default_factory=list)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.ensure_db()
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    RECEIPT_IMPORT_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Warehouse System API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
RECEIPT_IMPORT_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_ROOT)), name="uploads")


def _sanitize_filename(filename: Optional[str]) -> str:
    return Path(filename or "receipt").name


def _build_receipt_image_path(extension: str) -> Path:
    return RECEIPT_IMPORT_DIR / f"{uuid4().hex}.{extension}"


def _build_data_url(content: bytes, extension: str) -> str:
    import base64

    mime_type = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
    }.get(extension, "image/png")
    encoded = base64.b64encode(content).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _absolute_upload_url(path: str, request_url: Optional[str] = None) -> str:
    normalized = path.lstrip("/")
    if request_url:
        return f"{request_url.rstrip('/')}/uploads/{normalized}"
    return f"/uploads/{normalized}"


def _attach_image_url(record: Optional[dict], request: Optional[Request] = None) -> Optional[dict]:
    if not record:
        return None

    result = dict(record)
    image_path = str(result.get("imagePath") or "").strip()
    if not image_path:
        result["imageUrl"] = ""
        return result

    base_url = ""
    if request is not None:
        base_url = str(request.base_url).rstrip("/")

    result["imageUrl"] = _absolute_upload_url(image_path, base_url)
    return result


def _detect_image_extension(content: bytes) -> Optional[str]:
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"

    if content.startswith(b"\xff\xd8\xff"):
        return "jpeg"

    if content.startswith(b"GIF87a") or content.startswith(b"GIF89a"):
        return "gif"

    if len(content) >= 12 and content[0:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "webp"

    return None


def _extract_json_payload(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    try:
        payload = json.loads(cleaned)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        candidate = cleaned[start : end + 1]
        payload = json.loads(candidate)
        if isinstance(payload, dict):
            return payload

    raise ValueError("模型返回内容不是有效 JSON")


def _normalize_ai_items(items: Any) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    if not isinstance(items, list):
        return normalized

    for item in items:
        if not isinstance(item, dict):
            continue

        name = str(item.get("name") or "").strip()
        if not name:
            continue

        try:
            quantity = int(item.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1
        if quantity <= 0:
            quantity = 1

        normalized.append(
            {
                "name": name,
                "quantity": quantity,
                "storageLocation": str(item.get("storageLocation") or "").strip(),
                "note": str(item.get("note") or "").strip(),
            }
        )

    merged: list[dict[str, object]] = []
    for item in normalized:
        same_item = next(
            (
                existing
                for existing in merged
                if existing["name"] == item["name"]
                and existing["storageLocation"] == item["storageLocation"]
                and existing["note"] == item["note"]
            ),
            None,
        )
        if same_item:
            same_item["quantity"] = int(same_item["quantity"]) + int(item["quantity"])
        else:
            merged.append(item)

    return merged


async def _resolve_lm_studio_model(client: httpx.AsyncClient) -> str:
    if LM_STUDIO_MODEL:
        return LM_STUDIO_MODEL

    response = await client.get("/models")
    response.raise_for_status()
    payload = response.json()
    models = payload.get("data") if isinstance(payload, dict) else []
    for model in models or []:
        if isinstance(model, dict) and model.get("id"):
            return str(model["id"])

    raise HTTPException(status_code=503, detail="未能从 LM Studio 读取可用模型，请先加载一个多模态模型")


async def _extract_receipt_draft(content: bytes, extension: str, original_filename: str) -> dict[str, object]:
    data_url = _build_data_url(content, extension)
    prompt = (
        "你是一个中文 OCR 和商品信息提取助手。"
        "请从这张收货/购物截图中识别商品名称和数量，忽略价格、运费、优惠、地址、手机号、订单号、条形码、物流单号等无关信息。"
        "如果商品数量没有明确显示，数量默认为 1。"
        "如果同一个商品在截图里出现多次，请把数量合并。"
        "如果存在规格差异，但名称明显相同，也可以合并为同一项。"
        "请只输出严格 JSON，不要输出 Markdown 代码块，不要输出解释性文字。"
        "JSON 结构如下："
        "{\"note\":\"可选的简短说明\",\"items\":[{\"name\":\"商品名称\",\"quantity\":1,\"storageLocation\":\"\",\"note\":\"\"}]}"
        "其中 items 至少包含 1 个条目。"
    )

    headers = {}
    if LM_STUDIO_API_KEY:
        headers["Authorization"] = f"Bearer {LM_STUDIO_API_KEY}"

    async with httpx.AsyncClient(base_url=LM_STUDIO_BASE_URL, timeout=LM_STUDIO_TIMEOUT, headers=headers) as client:
        model = await _resolve_lm_studio_model(client)
        response = await client.post(
            "/chat/completions",
            json={
                "model": model,
                "temperature": 0,
                "max_tokens": 1200,
                "messages": [
                    {
                        "role": "system",
                        "content": "你只返回 JSON，不要返回额外说明。",
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_url,
                                },
                            },
                        ],
                    },
                ],
            },
        )
        response.raise_for_status()
        payload = response.json()

    choices = payload.get("choices") if isinstance(payload, dict) else None
    message = choices[0].get("message") if choices else None
    content_text = ""
    if isinstance(message, dict):
        content_text = str(message.get("content") or "").strip()

    parsed = _extract_json_payload(content_text)
    note = str(parsed.get("note") or "").strip()
    items = _normalize_ai_items(parsed.get("items"))

    if not items:
        items = [
            {
                "name": original_filename.rsplit(".", 1)[0] or "未命名商品",
                "quantity": 1,
                "storageLocation": "",
                "note": "模型未提取到清晰商品条目，请手动校对",
            }
        ]
        note = note or "模型未提取到清晰商品条目，请手动校对"

    return {
        "note": note,
        "items": items,
    }


async def _store_receipt_image(file: UploadFile) -> dict:
    original_filename = _sanitize_filename(file.filename)
    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="上传文件为空")

    if len(content) > MAX_RECEIPT_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过 5MB")

    detected_type = _detect_image_extension(content)
    extension = ALLOWED_IMAGE_TYPES.get(detected_type or "")
    if not extension:
        raise HTTPException(status_code=400, detail="仅支持上传 PNG、JPG、GIF 或 WEBP 图片")

    target_path = _build_receipt_image_path(extension)
    target_path.write_bytes(content)

    return {
        "original_filename": original_filename,
        "image_path": f"receipt-imports/{target_path.name}",
    }


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/login")
def login(payload: LoginRequest) -> dict:
    # 按照需求：默认用户名和密码均设为“admin”
    if payload.username == "admin" and payload.password == "admin":
        return {
            "token": "mock-token-admin",
            "user": {
                "username": "admin",
                "role": "管理员",
                "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=admin"
            }
        }
    raise HTTPException(status_code=401, detail="用户名或密码错误")


@app.get("/api/bootstrap")
def bootstrap() -> dict:
    return {
        "summary": db.get_summary(),
        "locations": db.get_all_storage_locations(),
        "products": db.get_all_products(),
        "transactions": db.get_all_transactions(),
    }


@app.get("/api/summary")
def summary() -> dict:
    return db.get_summary()


@app.get("/api/products")
def list_products() -> list[dict]:
    return db.get_all_products()


@app.get("/api/products/{product_id}")
def get_product(product_id: int) -> dict:
    product = db.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="货物不存在")
    return product


@app.patch("/api/products/{product_id}")
def update_product(product_id: int, payload: ProductUpdate) -> dict:
    success, message = db.update_product(
        product_id,
        name=payload.name,
        quantity=payload.quantity,
        storage_location=payload.storageLocation,
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": success, "message": message}


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int) -> dict:
    success, message = db.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": success, "message": message}


@app.get("/api/storage-locations")
def list_storage_locations() -> list[dict]:
    return db.get_all_storage_locations()


@app.post("/api/storage-locations")
def add_storage_location(payload: StorageLocationCreate) -> dict:
    success, message = db.add_storage_location(payload.name.strip())
    status_code = 200 if success else 400
    return {
        "success": success,
        "message": message,
        "status_code": status_code,
    }


@app.get("/api/transactions")
def list_transactions() -> list[dict]:
    return db.get_all_transactions()


@app.get("/api/location-stats")
def location_stats() -> list[dict]:
    return db.get_location_stats()


@app.get("/api/location-stats/{storage_location}")
def location_detail(storage_location: str) -> dict:
    return {
        "storageLocation": storage_location,
        "summary": db.get_summary(),
        "products": db.get_products_by_location(storage_location),
    }


@app.get("/api/search")
def search(
    name: str = "",
    storage_location: str = "",
    start_date: str = "",
    end_date: str = "",
) -> list[dict]:
    return db.search_products(
        name_keyword=name.strip(),
        storage_location=storage_location.strip(),
        start_date=start_date.strip(),
        end_date=end_date.strip(),
    )


@app.post("/api/check-product")
def check_product(payload: CheckProductRequest) -> dict:
    return db.check_product_by_name(payload.name.strip())


@app.post("/api/inbound")
def inbound(payload: InboundCreate) -> dict:
    success, message, product_id = db.create_product(
        payload.name.strip(),
        payload.quantity,
        payload.storageLocation.strip(),
        payload.note.strip(),
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {
        "success": True,
        "message": message,
        "productId": product_id,
    }


@app.post("/api/outbound")
def outbound(payload: OutboundCreate) -> dict:
    success, message = db.outbound_product(
        payload.productId,
        payload.quantity,
        payload.note.strip(),
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}


@app.get("/api/receipt-imports")
def list_receipt_imports(request: Request) -> list[dict]:
    records = db.get_all_receipt_imports()
    return [_attach_image_url(record, request) for record in records]


@app.get("/api/receipt-imports/{import_id}")
def get_receipt_import(import_id: int, request: Request) -> dict:
    record = db.get_receipt_import_by_id(import_id)
    if not record:
        raise HTTPException(status_code=404, detail="截图导入草稿不存在")
    return _attach_image_url(record, request) or record


@app.post("/api/receipt-imports")
async def create_receipt_import(request: Request, file: UploadFile = File(...)) -> dict:
    stored = await _store_receipt_image(file)
    record = db.create_receipt_import(stored["original_filename"], stored["image_path"])

    try:
        image_path = UPLOAD_ROOT / stored["image_path"]
        content = image_path.read_bytes()
        extension = image_path.suffix.lstrip(".").lower() or "png"
        draft = await _extract_receipt_draft(content, extension, stored["original_filename"])
        record = db.update_receipt_import(record["id"], draft) or record
    except Exception as exc:
        fallback_draft = {
            "note": f"模型识别失败，请手动校对：{exc}",
            "items": [
                {
                    "name": stored["original_filename"].rsplit(".", 1)[0] or "未命名商品",
                    "quantity": 1,
                    "storageLocation": "",
                    "note": "模型识别失败，请手动校对",
                }
            ],
        }
        record = db.update_receipt_import(record["id"], fallback_draft) or record
    return _attach_image_url(record, request) or record


@app.patch("/api/receipt-imports/{import_id}")
def update_receipt_import(import_id: int, payload: ReceiptImportDraftUpdate, request: Request) -> dict:
    draft = {
        "note": payload.note.strip(),
        "items": [
            {
                "name": item.name.strip(),
                "quantity": item.quantity,
                "storageLocation": item.storageLocation.strip(),
                "note": item.note.strip(),
            }
            for item in payload.items
        ],
    }
    record = db.update_receipt_import(import_id, draft)
    if not record:
        raise HTTPException(status_code=404, detail="截图导入草稿不存在")
    return _attach_image_url(record, request) or record


@app.post("/api/receipt-imports/{import_id}/confirm")
def confirm_receipt_import(import_id: int) -> dict:
    success, message, payload = db.confirm_receipt_import(import_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {
        "success": True,
        "message": message,
        **(payload or {}),
    }


def main() -> None:
    import uvicorn

    db.ensure_db()
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
