from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("WAREHOUSE_DB_PATH", str(BASE_DIR / "warehouse.db"))).expanduser().resolve()
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def connection() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def _table_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    return [row["name"] for row in cursor.fetchall()]


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


def _migrate_legacy_schema(conn: sqlite3.Connection) -> bool:
    columns = _table_columns(conn, "products")
    if "sku" not in columns:
        return False

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS storage_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        INSERT OR IGNORE INTO storage_locations (name)
        SELECT DISTINCT location FROM products WHERE location IS NOT NULL AND location != '';

        ALTER TABLE products RENAME TO products_old;

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER DEFAULT 0,
            storage_location TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        INSERT INTO products (id, name, quantity, storage_location, created_at)
        SELECT id, name, quantity, location, created_at FROM products_old;

        DROP TABLE products_old;

        CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
        CREATE INDEX IF NOT EXISTS idx_products_storage_location ON products(storage_location);
        CREATE INDEX IF NOT EXISTS idx_transactions_product_id ON transactions(product_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
        CREATE INDEX IF NOT EXISTS idx_receipt_imports_status ON receipt_imports(status);
        CREATE INDEX IF NOT EXISTS idx_receipt_imports_created_at ON receipt_imports(created_at);
        """
    )
    conn.commit()
    return True


def ensure_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('products', 'transactions', 'storage_locations', 'receipt_imports')"
        )
        tables = {row["name"] for row in cursor.fetchall()}
        if not tables:
            _ensure_schema(conn)
            return

        if "products" in tables and "sku" in _table_columns(conn, "products"):
            _migrate_legacy_schema(conn)

        if (
            "storage_locations" not in tables
            or "transactions" not in tables
            or "receipt_imports" not in tables
        ):
            _ensure_schema(conn)


def serialize_product(row: sqlite3.Row) -> Dict[str, object]:
    return {
        "id": row["id"],
        "name": row["name"],
        "quantity": row["quantity"],
        "storageLocation": row["storage_location"] or "",
        "createdAt": row["created_at"],
    }


def serialize_transaction(row: sqlite3.Row) -> Dict[str, object]:
    storage_location = row["storage_location"] if "storage_location" in row.keys() else ""
    return {
        "id": row["id"],
        "productId": row["product_id"],
        "productName": row["product_name"],
        "type": row["type"],
        "quantity": row["quantity"],
        "note": row["note"] or "",
        "storageLocation": storage_location or "",
        "createdAt": row["created_at"],
    }


def serialize_location(row: sqlite3.Row) -> Dict[str, object]:
    return {"id": row["id"], "name": row["name"]}


def _parse_json(value: Any, fallback: Any) -> Any:
    if value in (None, ""):
        return fallback

    if isinstance(value, (dict, list)):
        return value

    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback

    return parsed


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_quantity(value: Any) -> int:
    try:
        quantity = int(value)
    except (TypeError, ValueError):
        return 1

    return quantity if quantity > 0 else 1


def _normalize_receipt_item(value: Any) -> Dict[str, object]:
    item = value if isinstance(value, dict) else {}
    return {
        "name": _normalize_text(item.get("name")),
        "quantity": _normalize_quantity(item.get("quantity", 1)),
        "storageLocation": _normalize_text(item.get("storageLocation")),
        "note": _normalize_text(item.get("note")),
    }


def _normalize_receipt_draft(value: Any) -> Dict[str, object]:
    draft = value if isinstance(value, dict) else {}
    items = draft.get("items", [])
    normalized_items = [_normalize_receipt_item(item) for item in items if isinstance(item, dict)]
    if not normalized_items:
        normalized_items = [_normalize_receipt_item({})]

    return {
        "note": _normalize_text(draft.get("note")),
        "items": normalized_items,
    }


def _default_receipt_draft() -> Dict[str, object]:
    return {
        "note": "",
        "items": [_normalize_receipt_item({})],
    }


def _serialize_receipt_import(row: sqlite3.Row, include_draft: bool = False) -> Dict[str, object]:
    draft = _normalize_receipt_draft(_parse_json(row["draft_json"], _default_receipt_draft()))
    valid_items = [item for item in draft["items"] if item["name"]]

    payload: Dict[str, object] = {
        "id": row["id"],
        "originalFilename": row["original_filename"],
        "imagePath": row["image_path"],
        "imageUrl": f"/uploads/{row['image_path']}" if row["image_path"] else "",
        "status": row["status"],
        "createdAt": row["created_at"],
        "confirmedAt": row["confirmed_at"] or "",
        "itemCount": len(valid_items),
    }

    if include_draft:
        payload.update(draft)

    return payload


def _insert_product_and_transaction(
    cursor: sqlite3.Cursor,
    name: str,
    quantity: int,
    storage_location: str,
    note: str = "",
) -> int:
    cursor.execute(
        "INSERT INTO products (name, quantity, storage_location) VALUES (?, ?, ?)",
        (name, quantity, storage_location),
    )
    product_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO transactions (product_id, type, quantity, note) VALUES (?, 'IN', ?, ?)",
        (product_id, quantity, note),
    )
    return int(product_id)


def get_all_products() -> List[Dict[str, object]]:
    with connection() as conn:
        rows = conn.execute("SELECT * FROM products ORDER BY created_at DESC, id DESC").fetchall()
        return [serialize_product(row) for row in rows]


def get_product_by_id(product_id: int) -> Optional[Dict[str, object]]:
    with connection() as conn:
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        return serialize_product(row) if row else None


def get_all_storage_locations() -> List[Dict[str, object]]:
    with connection() as conn:
        rows = conn.execute("SELECT * FROM storage_locations ORDER BY name ASC").fetchall()
        return [serialize_location(row) for row in rows]


def add_storage_location(name: str) -> Tuple[bool, str]:
    with connection() as conn:
        try:
            conn.execute("INSERT INTO storage_locations (name) VALUES (?)", (name,))
            conn.commit()
            return True, "存储位置添加成功"
        except sqlite3.IntegrityError:
            return False, "存储位置已存在"
        except Exception as exc:
            return False, f"添加失败: {exc}"


def create_product(name: str, quantity: int, storage_location: str, note: str = "") -> Tuple[bool, str, Optional[int]]:
    with connection() as conn:
        try:
            cursor = conn.cursor()
            product_id = _insert_product_and_transaction(cursor, name, quantity, storage_location, note)
            conn.commit()
            return True, f"货物 {name} 创建成功，入库 {quantity} 件", product_id
        except Exception as exc:
            conn.rollback()
            return False, f"操作失败: {exc}", None


def outbound_product(product_id: int, quantity: int, note: str = "") -> Tuple[bool, str]:
    with connection() as conn:
        try:
            cursor = conn.cursor()
            product = cursor.execute(
                "SELECT id, name, quantity, storage_location FROM products WHERE id = ?",
                (product_id,),
            ).fetchone()
            if not product:
                return False, "货物不存在"
            if product["quantity"] < quantity:
                return False, f"库存不足，当前库存: {product['quantity']} 件"

            new_quantity = product["quantity"] - quantity
            cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))
            cursor.execute(
                "INSERT INTO transactions (product_id, type, quantity, note) VALUES (?, 'OUT', ?, ?)",
                (product_id, quantity, note),
            )
            conn.commit()
            return True, f"货物 {product['name']} 出库 {quantity} 件成功"
        except Exception as exc:
            conn.rollback()
            return False, f"操作失败: {exc}"


def delete_product(product_id: int) -> Tuple[bool, str]:
    with connection() as conn:
        try:
            cursor = conn.cursor()
            # 级联删除相关的交易记录
            cursor.execute("DELETE FROM transactions WHERE product_id = ?", (product_id,))
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            return True, "货物已删除"
        except Exception as exc:
            conn.rollback()
            return False, f"删除失败: {exc}"


def update_product(
    product_id: int, 
    name: str = None, 
    quantity: int = None, 
    storage_location: str = None,
    # note 存放在 transactions 或者作为 metadata，当前 products 表没有 note 字段
    # 为了简化，只更新 products 表已有字段
) -> Tuple[bool, str]:
    with connection() as conn:
        try:
            cursor = conn.cursor()
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if quantity is not None:
                updates.append("quantity = ?")
                params.append(quantity)
            if storage_location is not None:
                updates.append("storage_location = ?")
                params.append(storage_location)
            
            if not updates:
                return True, "没有需要更新的内容"
            
            params.append(product_id)
            query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            return True, "货物信息已更新"
        except Exception as exc:
            conn.rollback()
            return False, f"更新失败: {exc}"


def search_products(
    name_keyword: str = "",
    storage_location: str = "",
    start_date: str = "",
    end_date: str = "",
) -> List[Dict[str, object]]:
    query = """
        SELECT DISTINCT p.*
        FROM products p
        LEFT JOIN transactions t ON p.id = t.product_id
        WHERE 1=1
    """
    params: List[object] = []

    if name_keyword:
        query += " AND p.name LIKE ?"
        params.append(f"%{name_keyword}%")
    if storage_location:
        query += " AND p.storage_location = ?"
        params.append(storage_location)
    if start_date:
        query += " AND t.created_at >= ?"
        params.append(start_date)
    if end_date:
        query += " AND t.created_at <= ?"
        params.append(f"{end_date} 23:59:59")

    query += " ORDER BY p.name ASC, p.id DESC"

    with connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [serialize_product(row) for row in rows]


def get_all_transactions() -> List[Dict[str, object]]:
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT t.id, t.product_id, t.type, t.quantity, t.note, t.created_at,
                   p.name AS product_name, p.storage_location
            FROM transactions t
            JOIN products p ON t.product_id = p.id
            ORDER BY t.created_at DESC, t.id DESC
            """
        ).fetchall()
        return [serialize_transaction(row) for row in rows]


def get_location_stats() -> List[Dict[str, object]]:
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT
                storage_location,
                COUNT(*) AS product_count,
                SUM(quantity) AS total_quantity
            FROM products
            WHERE storage_location IS NOT NULL AND storage_location != ''
            GROUP BY storage_location
            ORDER BY storage_location ASC
            """
        ).fetchall()
        return [
            {
                "storageLocation": row["storage_location"],
                "productCount": row["product_count"],
                "totalQuantity": row["total_quantity"] or 0,
            }
            for row in rows
        ]


def get_products_by_location(storage_location: str) -> List[Dict[str, object]]:
    with connection() as conn:
        rows = conn.execute(
            "SELECT * FROM products WHERE storage_location = ? ORDER BY name ASC, id DESC",
            (storage_location,),
        ).fetchall()
        return [serialize_product(row) for row in rows]


def get_summary() -> Dict[str, object]:
    with connection() as conn:
        product_count = conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
        transaction_count = conn.execute("SELECT COUNT(*) AS c FROM transactions").fetchone()["c"]
        location_count = conn.execute(
            "SELECT COUNT(*) AS c FROM storage_locations"
        ).fetchone()["c"]
        total_quantity = conn.execute(
            "SELECT COALESCE(SUM(quantity), 0) AS total FROM products"
        ).fetchone()["total"]

        return {
            "totalProducts": product_count,
            "totalQuantity": total_quantity or 0,
            "totalLocations": location_count,
            "totalTransactions": transaction_count,
        }


def check_product_by_name(name: str) -> Dict[str, object]:
    if not name:
        return {"exists": False, "productId": None, "quantity": 0}

    matches = search_products(name_keyword=name)
    if matches:
        for product in matches:
            if product["name"] == name:
                return {
                    "exists": True,
                    "productId": product["id"],
                    "quantity": product["quantity"],
                }
        product = matches[0]
        return {
            "exists": True,
            "productId": product["id"],
            "quantity": product["quantity"],
        }

    return {"exists": False, "productId": None, "quantity": 0}


def get_all_receipt_imports() -> List[Dict[str, object]]:
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM receipt_imports
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
        return [_serialize_receipt_import(row) for row in rows]


def get_receipt_import_by_id(import_id: int) -> Optional[Dict[str, object]]:
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM receipt_imports WHERE id = ?",
            (import_id,),
        ).fetchone()
        return _serialize_receipt_import(row, include_draft=True) if row else None


def create_receipt_import(original_filename: str, image_path: str) -> Dict[str, object]:
    draft = _default_receipt_draft()
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO receipt_imports (original_filename, image_path, draft_json, status)
            VALUES (?, ?, ?, 'PENDING')
            """,
            (original_filename, image_path, json.dumps(draft, ensure_ascii=False)),
        )
        import_id = cursor.lastrowid
        conn.commit()

    record = get_receipt_import_by_id(int(import_id))
    if not record:
        raise RuntimeError("创建截图导入草稿失败")
    return record


def update_receipt_import(import_id: int, draft: Dict[str, object]) -> Optional[Dict[str, object]]:
    normalized_draft = _normalize_receipt_draft(draft)

    with connection() as conn:
        cursor = conn.cursor()
        row = cursor.execute(
            "SELECT id FROM receipt_imports WHERE id = ?",
            (import_id,),
        ).fetchone()
        if not row:
            return None

        cursor.execute(
            """
            UPDATE receipt_imports
            SET draft_json = ?, status = 'PENDING', confirmed_at = NULL
            WHERE id = ?
            """,
            (json.dumps(normalized_draft, ensure_ascii=False), import_id),
        )
        conn.commit()

    return get_receipt_import_by_id(import_id)


def confirm_receipt_import(import_id: int) -> Tuple[bool, str, Optional[Dict[str, object]]]:
    with connection() as conn:
        cursor = conn.cursor()
        row = cursor.execute(
            "SELECT * FROM receipt_imports WHERE id = ?",
            (import_id,),
        ).fetchone()
        if not row:
            return False, "截图导入草稿不存在", None

        if row["status"] == "CONFIRMED":
            return False, "该截图导入草稿已经确认过了", None

        draft = _normalize_receipt_draft(_parse_json(row["draft_json"], _default_receipt_draft()))
        items = [item for item in draft["items"] if item["name"]]
        if not items:
            return False, "草稿中没有可确认的货物", None

        created_product_ids: List[int] = []
        try:
            for item in items:
                created_product_id = _insert_product_and_transaction(
                    cursor,
                    item["name"],
                    item["quantity"],
                    item["storageLocation"],
                    item["note"],
                )
                created_product_ids.append(created_product_id)

            cursor.execute(
                """
                UPDATE receipt_imports
                SET status = 'CONFIRMED', confirmed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (import_id,),
            )
            conn.commit()
        except Exception as exc:
            conn.rollback()
            return False, f"确认导入失败: {exc}", None

    return (
        True,
        f"已确认 {len(created_product_ids)} 条截图导入记录",
        {
            "createdProductIds": created_product_ids,
            "createdCount": len(created_product_ids),
        },
    )
