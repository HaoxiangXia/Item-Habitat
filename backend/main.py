from __future__ import annotations

import json
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.db import ensure_db, get_db


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_ROOT = Path(os.getenv("WAREHOUSE_UPLOAD_DIR", str(BASE_DIR / "uploads")))
RECEIPT_IMPORT_DIR = UPLOAD_ROOT / "receipt-imports"


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_db()
    RECEIPT_IMPORT_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Item Habitat API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
RECEIPT_IMPORT_DIR.mkdir(parents=True, exist_ok=True)
ensure_db()
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_ROOT)), name="uploads")


class LoginRequest(BaseModel):
    username: str
    password: str


class SpaceCreate(BaseModel):
    name: str = Field(min_length=1)


class InboundCreate(BaseModel):
    name: str = Field(min_length=1)
    quantity: int = Field(default=1, ge=1)
    storageLocation: str = ""
    note: str = ""


class OutboundCreate(BaseModel):
    productId: str = Field(min_length=1)
    quantity: int = Field(default=1, ge=1)
    targetLocation: str = ""
    note: str = ""


class CheckProductRequest(BaseModel):
    name: str = ""


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    storageLocation: Optional[str] = None
    tags: Optional[Any] = None
    notes: Optional[str] = None


class ItemCreate(BaseModel):
    name: str
    categoryId: Optional[str] = None
    imageUrl: Optional[str] = None
    quantity: int = 1
    spaceId: Optional[str] = None
    status: str = "pending"
    tags: list[str] = Field(default_factory=list)
    deadline: Optional[str] = None
    notes: Optional[str] = None


class ReceiptImportItemUpdate(BaseModel):
    name: str = ""
    quantity: int = Field(default=1, ge=1)
    storageLocation: str = ""
    note: str = ""


class ReceiptImportDraftUpdate(BaseModel):
    note: str = ""
    items: list[ReceiptImportItemUpdate] = Field(default_factory=list)


def _space_id_for_name(db, name: str) -> Optional[str]:
    normalized = name.strip()
    if not normalized:
        return None
    row = db.execute("SELECT id FROM spaces WHERE name = ?", (normalized,)).fetchone()
    if row:
        return row["id"]
    space_id = str(uuid.uuid4())
    db.execute("INSERT INTO spaces (id, name) VALUES (?, ?)", (space_id, normalized))
    return space_id


def _space_name(db, space_id: Optional[str]) -> str:
    if not space_id:
        return ""
    row = db.execute("SELECT name FROM spaces WHERE id = ?", (space_id,)).fetchone()
    return row["name"] if row else ""


def _encode_tags(tags: Any) -> str:
    if isinstance(tags, str):
        values = [tag.strip() for tag in tags.split(",") if tag.strip()]
    elif isinstance(tags, list):
        values = [str(tag).strip() for tag in tags if str(tag).strip()]
    else:
        values = []
    return json.dumps(values, ensure_ascii=False)


def _serialize_product(db, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "quantity": row["quantity"] or 0,
        "storageLocation": _space_name(db, row.get("spaceId")),
        "createdAt": row.get("createdAt"),
        "updatedAt": row.get("updatedAt") or row.get("createdAt"),
        "tags": row.get("tags") or [],
        "note": row.get("notes") or "",
        "status": row.get("status") or "pending",
    }


def _list_products(db) -> list[dict[str, Any]]:
    rows = db.execute("SELECT * FROM items WHERE status != 'archived' ORDER BY createdAt DESC, id DESC").fetchall()
    return [_serialize_product(db, row) for row in rows]


def _get_product(db, item_id: str) -> Optional[dict[str, Any]]:
    row = db.execute("SELECT * FROM items WHERE id = ?", (str(item_id),)).fetchone()
    return _serialize_product(db, row) if row else None


def _serialize_log(db, row: dict[str, Any]) -> dict[str, Any]:
    item = db.execute("SELECT * FROM items WHERE id = ?", (row["itemId"],)).fetchone()
    product_name = item["name"] if item else "已删除物品"
    action_type = row["actionType"]
    is_in = action_type in {"create", "return", "store"}
    quantity = abs(row.get("quantityDelta") or 0) or 1
    storage_location = _space_name(db, row.get("toSpaceId") or (item or {}).get("spaceId"))
    return {
        "id": row["id"],
        "productId": row["itemId"],
        "productName": product_name,
        "type": "IN" if is_in else "OUT",
        "quantity": quantity,
        "note": row.get("detail") or "",
        "storageLocation": storage_location,
        "targetLocation": _space_name(db, row.get("toSpaceId")),
        "createdAt": row["createdAt"],
    }


def _default_receipt_draft(filename: str = "") -> dict[str, Any]:
    name = Path(filename).stem or "未命名物品"
    return {"note": "", "items": [{"name": name, "quantity": 1, "storageLocation": "", "note": ""}]}


def _normalize_draft(value: Any, filename: str = "") -> dict[str, Any]:
    draft = value if isinstance(value, dict) else {}
    items = draft.get("items") if isinstance(draft.get("items"), list) else []
    normalized = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        quantity = int(item.get("quantity") or 1)
        normalized.append(
            {
                "name": name,
                "quantity": max(quantity, 1),
                "storageLocation": str(item.get("storageLocation") or "").strip(),
                "note": str(item.get("note") or "").strip(),
            }
        )
    if not normalized:
        normalized = _default_receipt_draft(filename)["items"]
    return {"note": str(draft.get("note") or "").strip(), "items": normalized}


def _serialize_receipt(row: dict[str, Any], request: Optional[Request] = None, include_draft: bool = False) -> dict[str, Any]:
    image_url = row["imageUrl"] or ""
    if image_url.startswith("receipt-imports/"):
        base_url = str(request.base_url).rstrip("/") if request else ""
        image_url = f"{base_url}/uploads/{image_url}" if base_url else f"/uploads/{image_url}"
    draft = _normalize_draft(json.loads(row["draftJson"]), row.get("originalFilename") or "")
    payload = {
        "id": row["id"],
        "originalFilename": row.get("originalFilename") or "",
        "imagePath": row["imageUrl"],
        "imageUrl": image_url,
        "status": "CONFIRMED" if row["status"] == "confirmed" else "PENDING",
        "createdAt": row["createdAt"],
        "confirmedAt": row.get("confirmedAt") or "",
        "itemCount": len([item for item in draft["items"] if item["name"]]),
    }
    if include_draft:
        payload.update(draft)
    return payload


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/login")
def login(payload: LoginRequest) -> dict[str, Any]:
    if payload.username == "admin" and payload.password == "admin":
        return {"token": "mock-token-admin", "user": {"username": "admin", "role": "管理员"}}
    raise HTTPException(status_code=401, detail="用户名或密码错误")


@app.get("/api/bootstrap")
def bootstrap() -> dict[str, Any]:
    with get_db() as db:
        products = _list_products(db)
        transactions = [_serialize_log(db, row) for row in db.execute("SELECT * FROM logs ORDER BY createdAt DESC").fetchall()]
        locations = db.execute("SELECT id, name FROM spaces ORDER BY name ASC").fetchall()
        return {"summary": _summary(products, locations, transactions), "locations": locations, "products": products, "transactions": transactions}


def _summary(products: list[dict[str, Any]], locations: list[dict[str, Any]], transactions: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "totalProducts": len(products),
        "totalQuantity": sum(int(product.get("quantity") or 0) for product in products),
        "totalLocations": len(locations),
        "totalTransactions": len(transactions),
    }


@app.get("/api/summary")
def summary() -> dict[str, int]:
    with get_db() as db:
        return _summary(
            _list_products(db),
            db.execute("SELECT id, name FROM spaces").fetchall(),
            db.execute("SELECT id FROM logs").fetchall(),
        )


@app.get("/api/items")
@app.get("/api/products")
def list_products() -> list[dict[str, Any]]:
    with get_db() as db:
        return _list_products(db)


@app.post("/api/items")
def create_item(item: ItemCreate) -> dict[str, str]:
    with get_db() as db:
        item_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO items (id, name, categoryId, imageUrl, quantity, spaceId, status, tags, deadline, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (item_id, item.name, item.categoryId, item.imageUrl, item.quantity, item.spaceId, item.status, _encode_tags(item.tags), item.deadline, item.notes),
        )
        db.execute(
            "INSERT INTO logs (id, itemId, actionType, quantityDelta, toSpaceId, toStatus, detail) VALUES (?, ?, 'create', ?, ?, ?, ?)",
            (str(uuid.uuid4()), item_id, item.quantity, item.spaceId, item.status, "创建物品"),
        )
        db.commit()
        return {"id": item_id}


@app.patch("/api/products/{product_id}")
def update_product(product_id: str, payload: ProductUpdate) -> dict[str, Any]:
    with get_db() as db:
        current = db.execute("SELECT * FROM items WHERE id = ?", (str(product_id),)).fetchone()
        if not current:
            raise HTTPException(status_code=404, detail="物品不存在")
        updates = []
        params: list[Any] = []
        if payload.name is not None:
            updates.append("name = ?")
            params.append(payload.name)
        if payload.quantity is not None:
            updates.append("quantity = ?")
            params.append(payload.quantity)
        if payload.storageLocation is not None:
            updates.append("spaceId = ?")
            params.append(_space_id_for_name(db, payload.storageLocation))
        if payload.tags is not None:
            updates.append("tags = ?")
            params.append(_encode_tags(payload.tags))
        if payload.notes is not None:
            updates.append("notes = ?")
            params.append(payload.notes)
        if updates:
            updates.append("updatedAt = CURRENT_TIMESTAMP")
            params.append(str(product_id))
            db.execute(f"UPDATE items SET {', '.join(updates)} WHERE id = ?", params)
            db.execute(
                "INSERT INTO logs (id, itemId, actionType, detail) VALUES (?, ?, 'update', ?)",
                (str(uuid.uuid4()), str(product_id), "更新物品信息"),
            )
            db.commit()
        return {"success": True, "message": "物品信息已更新"}


@app.delete("/api/products/{product_id}")
def delete_product(product_id: str) -> dict[str, Any]:
    with get_db() as db:
        db.execute("UPDATE items SET status = 'archived', updatedAt = CURRENT_TIMESTAMP WHERE id = ?", (str(product_id),))
        db.execute("INSERT INTO logs (id, itemId, actionType, detail) VALUES (?, ?, 'archive', ?)", (str(uuid.uuid4()), str(product_id), "归档物品"))
        db.commit()
        return {"success": True, "message": "物品已归档"}


@app.get("/api/storage-locations")
def list_storage_locations() -> list[dict[str, Any]]:
    with get_db() as db:
        return db.execute("SELECT id, name FROM spaces ORDER BY name ASC").fetchall()


@app.post("/api/storage-locations")
def create_storage_location(payload: SpaceCreate) -> dict[str, Any]:
    with get_db() as db:
        space_id = _space_id_for_name(db, payload.name)
        db.commit()
        return {"success": True, "message": "空间添加成功", "id": space_id}


@app.post("/api/inbound")
def inbound(payload: InboundCreate) -> dict[str, Any]:
    with get_db() as db:
        space_id = _space_id_for_name(db, payload.storageLocation)
        item_id = str(uuid.uuid4())
        status = "stored" if space_id else "pending"
        db.execute(
            "INSERT INTO items (id, name, quantity, spaceId, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (item_id, payload.name.strip(), payload.quantity, space_id, status, payload.note.strip()),
        )
        db.execute(
            "INSERT INTO logs (id, itemId, actionType, quantityDelta, toSpaceId, toStatus, detail) VALUES (?, ?, 'create', ?, ?, ?, ?)",
            (str(uuid.uuid4()), item_id, payload.quantity, space_id, status, payload.note.strip()),
        )
        db.commit()
        return {"success": True, "message": f"物品 {payload.name} 已创建", "productId": item_id}


@app.post("/api/outbound")
def outbound(payload: OutboundCreate) -> dict[str, Any]:
    with get_db() as db:
        item = db.execute("SELECT * FROM items WHERE id = ?", (str(payload.productId),)).fetchone()
        if not item:
            raise HTTPException(status_code=404, detail="物品不存在")
        if int(item["quantity"] or 0) < payload.quantity:
            raise HTTPException(status_code=400, detail=f"数量不足，当前数量: {item['quantity']}")
        new_quantity = int(item["quantity"] or 0) - payload.quantity
        db.execute(
            "UPDATE items SET quantity = ?, status = CASE WHEN ? = 0 THEN 'taken' ELSE status END, lastTakenAt = CURRENT_TIMESTAMP, updatedAt = CURRENT_TIMESTAMP WHERE id = ?",
            (new_quantity, new_quantity, str(payload.productId)),
        )
        db.execute(
            "INSERT INTO logs (id, itemId, actionType, quantityDelta, fromSpaceId, detail) VALUES (?, ?, 'take', ?, ?, ?)",
            (str(uuid.uuid4()), str(payload.productId), -payload.quantity, item.get("spaceId"), payload.note.strip()),
        )
        db.commit()
        return {"success": True, "message": "取出成功"}


@app.get("/api/transactions")
def list_transactions() -> list[dict[str, Any]]:
    with get_db() as db:
        return [_serialize_log(db, row) for row in db.execute("SELECT * FROM logs ORDER BY createdAt DESC").fetchall()]


@app.get("/api/location-stats")
def location_stats() -> list[dict[str, Any]]:
    with get_db() as db:
        return [
            {"storageLocation": space["name"], "productCount": space["productCount"], "totalQuantity": space["totalQuantity"] or 0}
            for space in db.execute(
                """
                SELECT s.name, COUNT(i.id) AS productCount, COALESCE(SUM(i.quantity), 0) AS totalQuantity
                FROM spaces s
                LEFT JOIN items i ON i.spaceId = s.id AND i.status != 'archived'
                GROUP BY s.id, s.name
                HAVING productCount > 0
                ORDER BY s.name ASC
                """
            ).fetchall()
        ]


@app.get("/api/location-stats/{storage_location}")
def location_detail(storage_location: str) -> dict[str, Any]:
    with get_db() as db:
        space = db.execute("SELECT * FROM spaces WHERE name = ?", (storage_location,)).fetchone()
        products = []
        if space:
            rows = db.execute("SELECT * FROM items WHERE spaceId = ? AND status != 'archived'", (space["id"],)).fetchall()
            products = [_serialize_product(db, row) for row in rows]
        return {"storageLocation": storage_location, "summary": summary(), "products": products}


@app.get("/api/search")
def search(name: str = "", storage_location: str = "", start_date: str = "", end_date: str = "") -> list[dict[str, Any]]:
    with get_db() as db:
        products = _list_products(db)
        if name:
            products = [product for product in products if name.lower() in product["name"].lower()]
        if storage_location:
            products = [product for product in products if product["storageLocation"] == storage_location]
        return products


@app.post("/api/check-product")
def check_product(payload: CheckProductRequest) -> dict[str, Any]:
    with get_db() as db:
        row = db.execute("SELECT id, quantity FROM items WHERE name = ? AND status != 'archived' LIMIT 1", (payload.name.strip(),)).fetchone()
        return {"exists": bool(row), "productId": row["id"] if row else None, "quantity": row["quantity"] if row else 0}


@app.get("/api/receipt-imports")
def list_receipt_imports(request: Request) -> list[dict[str, Any]]:
    with get_db() as db:
        rows = db.execute("SELECT * FROM receipt_imports ORDER BY createdAt DESC").fetchall()
        return [_serialize_receipt(row, request) for row in rows]


@app.get("/api/receipt-imports/{import_id}")
def get_receipt_import(import_id: str, request: Request) -> dict[str, Any]:
    with get_db() as db:
        row = db.execute("SELECT * FROM receipt_imports WHERE id = ?", (str(import_id),)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="截图导入草稿不存在")
        return _serialize_receipt(row, request, include_draft=True)


@app.post("/api/receipt-imports")
async def create_receipt_import(request: Request, file: UploadFile = File(...)) -> dict[str, Any]:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="上传文件为空")
    suffix = Path(file.filename or "receipt.png").suffix or ".png"
    import_id = str(uuid.uuid4())
    filename = f"{import_id}{suffix}"
    target = RECEIPT_IMPORT_DIR / filename
    target.write_bytes(content)
    image_path = f"receipt-imports/{filename}"
    draft = _default_receipt_draft(file.filename or "")
    with get_db() as db:
        db.execute(
            "INSERT INTO receipt_imports (id, originalFilename, imageUrl, draftJson) VALUES (?, ?, ?, ?)",
            (import_id, file.filename or filename, image_path, json.dumps(draft, ensure_ascii=False)),
        )
        db.commit()
        row = db.execute("SELECT * FROM receipt_imports WHERE id = ?", (import_id,)).fetchone()
        return _serialize_receipt(row, request, include_draft=True)


@app.patch("/api/receipt-imports/{import_id}")
def update_receipt_import(import_id: str, payload: ReceiptImportDraftUpdate, request: Request) -> dict[str, Any]:
    draft = {
        "note": payload.note.strip(),
        "items": [
            {"name": item.name.strip(), "quantity": item.quantity, "storageLocation": item.storageLocation.strip(), "note": item.note.strip()}
            for item in payload.items
        ],
    }
    with get_db() as db:
        db.execute("UPDATE receipt_imports SET draftJson = ?, status = 'draft', confirmedAt = NULL WHERE id = ?", (json.dumps(draft, ensure_ascii=False), str(import_id)))
        db.commit()
        row = db.execute("SELECT * FROM receipt_imports WHERE id = ?", (str(import_id),)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="截图导入草稿不存在")
        return _serialize_receipt(row, request, include_draft=True)


@app.post("/api/receipt-imports/{import_id}/confirm")
def confirm_receipt_import(import_id: str) -> dict[str, Any]:
    with get_db() as db:
        row = db.execute("SELECT * FROM receipt_imports WHERE id = ?", (str(import_id),)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="截图导入草稿不存在")
        if row["status"] == "confirmed":
            raise HTTPException(status_code=400, detail="该草稿已经确认")
        draft = _normalize_draft(json.loads(row["draftJson"]), row.get("originalFilename") or "")
        created_ids = []
        for item in draft["items"]:
            if not item["name"]:
                continue
            space_id = _space_id_for_name(db, item["storageLocation"])
            item_id = str(uuid.uuid4())
            status = "stored" if space_id else "pending"
            db.execute(
                "INSERT INTO items (id, name, quantity, spaceId, status, notes, source, sourceId) VALUES (?, ?, ?, ?, ?, ?, 'receipt_import', ?)",
                (item_id, item["name"], item["quantity"], space_id, status, item["note"], str(import_id)),
            )
            db.execute(
                "INSERT INTO logs (id, itemId, actionType, quantityDelta, toSpaceId, toStatus, detail) VALUES (?, ?, 'create', ?, ?, ?, ?)",
                (str(uuid.uuid4()), item_id, item["quantity"], space_id, status, "截图导入创建"),
            )
            created_ids.append(item_id)
        db.execute("UPDATE receipt_imports SET status = 'confirmed', confirmedAt = CURRENT_TIMESTAMP WHERE id = ?", (str(import_id),))
        db.commit()
        return {"success": True, "message": f"已确认 {len(created_ids)} 条截图导入记录", "createdProductIds": created_ids, "createdCount": len(created_ids)}


def main() -> None:
    import uvicorn

    ensure_db()
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
