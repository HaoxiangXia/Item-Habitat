from __future__ import annotations

import json
import os
import sqlite3
import uuid
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("WAREHOUSE_DB_PATH", str(BASE_DIR / "warehouse.db"))).expanduser().resolve()
SCHEMA_PATH = BASE_DIR / "backend" / "schema.sql"


def table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    return cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
        (table_name,),
    ).fetchone() is not None


def get_space_id(cursor: sqlite3.Cursor, name: str) -> str:
    row = cursor.execute("SELECT id FROM spaces WHERE name = ?", (name,)).fetchone()
    if row:
        return str(row[0])
    space_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO spaces (id, name) VALUES (?, ?)", (space_id, name))
    return space_id


def migrate() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        if not table_exists(cursor, "products"):
            conn.commit()
            return

        item_count = cursor.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        if item_count:
            conn.commit()
            return

        if table_exists(cursor, "storage_locations"):
            for (name,) in cursor.execute("SELECT name FROM storage_locations WHERE name IS NOT NULL AND name != ''").fetchall():
                get_space_id(cursor, name)

        item_map: dict[int, str] = {}
        for product_id, name, quantity, storage_location, created_at in cursor.execute(
            "SELECT id, name, quantity, storage_location, created_at FROM products"
        ).fetchall():
            item_id = str(product_id)
            item_map[product_id] = item_id
            space_id = get_space_id(cursor, storage_location) if storage_location else None
            status = "stored" if space_id else "pending"
            cursor.execute(
                """
                INSERT OR IGNORE INTO items (id, name, quantity, spaceId, status, createdAt)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (item_id, name, quantity, space_id, status, created_at),
            )

        if table_exists(cursor, "transactions"):
            for product_id, tx_type, quantity, note, target_location, created_at in cursor.execute(
                "SELECT product_id, type, quantity, note, target_location, created_at FROM transactions"
            ).fetchall():
                item_id = item_map.get(product_id)
                if not item_id:
                    continue
                action_type = "return" if tx_type == "IN" else "take"
                quantity_delta = quantity if tx_type == "IN" else -quantity
                cursor.execute(
                    """
                    INSERT INTO logs (id, itemId, actionType, quantityDelta, detail, createdAt)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (str(uuid.uuid4()), item_id, action_type, quantity_delta, note or target_location or "", created_at),
                )

        if table_exists(cursor, "receipt_imports"):
            columns = [row[1] for row in cursor.execute("PRAGMA table_info(receipt_imports)").fetchall()]
            if "draft_json" in columns:
                legacy_rows = cursor.execute(
                    "SELECT original_filename, image_path, draft_json, status, created_at, confirmed_at FROM receipt_imports"
                ).fetchall()
                cursor.execute("ALTER TABLE receipt_imports RENAME TO receipt_imports_legacy")
                cursor.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
                for original_filename, image_path, draft_json, status, created_at, confirmed_at in legacy_rows:
                    normalized_status = "confirmed" if str(status).upper() == "CONFIRMED" else "draft"
                    cursor.execute(
                        """
                        INSERT INTO receipt_imports (id, originalFilename, imageUrl, status, draftJson, createdAt, confirmedAt)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            str(uuid.uuid4()),
                            original_filename,
                            image_path,
                            normalized_status,
                            draft_json or json.dumps({"note": "", "items": []}, ensure_ascii=False),
                            created_at,
                            confirmed_at,
                        ),
                    )
                cursor.execute("DROP TABLE receipt_imports_legacy")

        cursor.executescript(
            """
            DROP TABLE IF EXISTS products;
            DROP TABLE IF EXISTS transactions;
            DROP TABLE IF EXISTS storage_locations;
            """
        )
        conn.commit()


if __name__ == "__main__":
    migrate()

