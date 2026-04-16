from __future__ import annotations

import imghdr
import os
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
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


class ReceiptImportItemUpdate(BaseModel):
    name: str = Field(default="")
    quantity: int = Field(default=1, ge=1)
    storageLocation: str = Field(default="")
    note: str = Field(default="")


class ReceiptImportDraftUpdate(BaseModel):
    note: str = Field(default="")
    items: List[ReceiptImportItemUpdate] = Field(default_factory=list)


UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
RECEIPT_IMPORT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Warehouse System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_ROOT)), name="uploads")


@app.on_event("startup")
def on_startup() -> None:
    db.ensure_db()
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    RECEIPT_IMPORT_DIR.mkdir(parents=True, exist_ok=True)


def _sanitize_filename(filename: Optional[str]) -> str:
    return Path(filename or "receipt").name


def _build_receipt_image_path(extension: str) -> Path:
    return RECEIPT_IMPORT_DIR / f"{uuid4().hex}.{extension}"


async def _store_receipt_image(file: UploadFile) -> dict:
    original_filename = _sanitize_filename(file.filename)
    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="上传文件为空")

    if len(content) > MAX_RECEIPT_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过 5MB")

    detected_type = imghdr.what(None, content)
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
def list_receipt_imports() -> list[dict]:
    return db.get_all_receipt_imports()


@app.get("/api/receipt-imports/{import_id}")
def get_receipt_import(import_id: int) -> dict:
    record = db.get_receipt_import_by_id(import_id)
    if not record:
        raise HTTPException(status_code=404, detail="截图导入草稿不存在")
    return record


@app.post("/api/receipt-imports")
async def create_receipt_import(file: UploadFile = File(...)) -> dict:
    stored = await _store_receipt_image(file)
    record = db.create_receipt_import(stored["original_filename"], stored["image_path"])
    return record


@app.patch("/api/receipt-imports/{import_id}")
def update_receipt_import(import_id: int, payload: ReceiptImportDraftUpdate) -> dict:
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
    return record


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
