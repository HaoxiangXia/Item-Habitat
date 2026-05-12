from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("WAREHOUSE_DB_PATH", str(BASE_DIR / "warehouse.db"))).expanduser().resolve()
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def _decode_tags(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []
    return parsed if isinstance(parsed, list) else []


def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for index, column in enumerate(cursor.description):
        value = row[index]
        result[column[0]] = _decode_tags(value) if column[0] == "tags" else value
    return result


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _table_columns(conn: sqlite3.Connection, table_name: str) -> list[str]:
    return [row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()]


def _table_empty(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
    return int(row["count"]) == 0


def _space_id_for_name(conn: sqlite3.Connection, name: str) -> str:
    existing = conn.execute("SELECT id FROM spaces WHERE name = ?", (name,)).fetchone()
    if existing:
        return str(existing["id"])

    import uuid

    space_id = str(uuid.uuid4())
    conn.execute("INSERT INTO spaces (id, name) VALUES (?, ?)", (space_id, name))
    return space_id


def _migrate_legacy_data(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "products") or not _table_empty(conn, "items"):
        return

    if _table_exists(conn, "storage_locations"):
        for row in conn.execute("SELECT name FROM storage_locations WHERE name IS NOT NULL AND name != ''").fetchall():
            _space_id_for_name(conn, row["name"])

    item_map: dict[Any, str] = {}
    for product in conn.execute(
        "SELECT id, name, quantity, storage_location, created_at FROM products"
    ).fetchall():
        item_id = str(product["id"])
        space_name = str(product["storage_location"] or "").strip()
        space_id = _space_id_for_name(conn, space_name) if space_name else None
        status = "stored" if space_id else "pending"
        item_map[product["id"]] = item_id
        conn.execute(
            """
            INSERT OR IGNORE INTO items (id, name, quantity, spaceId, status, createdAt)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
                product["name"],
                product["quantity"] or 0,
                space_id,
                status,
                product["created_at"],
            ),
        )

    if _table_exists(conn, "transactions"):
        import uuid

        for transaction in conn.execute(
            "SELECT product_id, type, quantity, note, target_location, created_at FROM transactions"
        ).fetchall():
            item_id = item_map.get(transaction["product_id"])
            if not item_id:
                continue
            action_type = "return" if transaction["type"] == "IN" else "take"
            quantity_delta = transaction["quantity"] if transaction["type"] == "IN" else -transaction["quantity"]
            conn.execute(
                """
                INSERT INTO logs (id, itemId, actionType, quantityDelta, detail, createdAt)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    item_id,
                    action_type,
                    quantity_delta,
                    transaction["note"] or "",
                    transaction["created_at"],
                ),
            )


def _migrate_legacy_receipt_imports(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "receipt_imports"):
        return

    columns = _table_columns(conn, "receipt_imports")
    if "draft_json" not in columns:
        return

    legacy_rows = conn.execute(
        """
        SELECT original_filename, image_path, draft_json, status, created_at, confirmed_at
        FROM receipt_imports
        """
    ).fetchall()
    conn.execute("ALTER TABLE receipt_imports RENAME TO receipt_imports_legacy")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    import uuid

    for row in legacy_rows:
        status = "confirmed" if str(row["status"]).upper() == "CONFIRMED" else "draft"
        conn.execute(
            """
            INSERT INTO receipt_imports (id, originalFilename, imageUrl, status, draftJson, createdAt, confirmedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                row["original_filename"],
                row["image_path"],
                status,
                row["draft_json"] or json.dumps({"note": "", "items": []}, ensure_ascii=False),
                row["created_at"],
                row["confirmed_at"],
            ),
        )

    conn.execute("DROP TABLE receipt_imports_legacy")


def ensure_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        _migrate_legacy_receipt_imports(conn)
        _migrate_legacy_data(conn)
        conn.commit()
