from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
from typing import Any

from trading_os.db.migrations import CREATE_SCHEMA, SCHEMA_VERSION
from trading_os.db.models import PersistentRecord, utc_now


def sqlite_path(database_url: str) -> Path:
    if database_url.startswith("sqlite:///"):
        raw_path = database_url.removeprefix("sqlite:///")
        if raw_path.startswith("data/") and _running_on_railway():
            return Path("/") / raw_path
        return Path(raw_path)
    return Path(database_url)


def _running_on_railway() -> bool:
    return any(
        os.getenv(name)
        for name in (
            "RAILWAY_ENVIRONMENT",
            "RAILWAY_ENVIRONMENT_ID",
            "RAILWAY_PROJECT_ID",
            "RAILWAY_SERVICE_ID",
        )
    )


class SQLiteStorage:
    def __init__(self, database_url: str = "sqlite:///data/trading_os.sqlite3") -> None:
        self.path = sqlite_path(database_url)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(CREATE_SCHEMA)
            connection.execute(
                "INSERT OR REPLACE INTO metadata(key, value) VALUES (?, ?)",
                ("schema_version", str(SCHEMA_VERSION)),
            )

    def save_record(self, record: PersistentRecord) -> PersistentRecord:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO records(category, record_id, payload_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record.category,
                    record.record_id,
                    json.dumps(record.payload, sort_keys=True),
                    record.created_at,
                    record.updated_at,
                ),
            )
        return record

    def latest_record(self, category: str) -> dict[str, Any] | None:
        records = self.list_records(category=category, limit=1, newest_first=True)
        return records[0] if records else None

    def list_records(
        self,
        category: str | None = None,
        limit: int = 100,
        newest_first: bool = False,
    ) -> list[dict[str, Any]]:
        order = "DESC" if newest_first else "ASC"
        params: list[Any] = []
        where = ""
        if category:
            where = "WHERE category = ?"
            params.append(category)
        params.append(limit)
        with self.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT category, record_id, payload_json, created_at, updated_at
                FROM records
                {where}
                ORDER BY created_at {order}
                LIMIT ?
                """,
                params,
            ).fetchall()
        return [
            {
                "category": row["category"],
                "record_id": row["record_id"],
                "payload": json.loads(row["payload_json"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def save_setting(self, key: str, value: dict[str, Any]) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO settings(key, value_json, updated_at) VALUES (?, ?, ?)",
                (key, json.dumps(value, sort_keys=True), utc_now()),
            )

    def get_setting(self, key: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT value_json FROM settings WHERE key = ?", (key,)
            ).fetchone()
        return json.loads(row["value_json"]) if row else None

    def list_settings(self) -> dict[str, dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute("SELECT key, value_json FROM settings").fetchall()
        return {row["key"]: json.loads(row["value_json"]) for row in rows}
