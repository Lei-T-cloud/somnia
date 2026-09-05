import sqlite3
from pathlib import Path


def merge_legacy_sqlite() -> None:
    from django.conf import settings

    current = Path(settings.DATABASES["default"]["NAME"])
    legacy = Path(settings.BASE_DIR) / "somnia_django.db"
    if not legacy.exists() or legacy.resolve() == current.resolve():
        return
    current.parent.mkdir(parents=True, exist_ok=True)
    if not current.exists():
        current.write_bytes(legacy.read_bytes())
        _retire(legacy)
        return
    src = sqlite3.connect(str(legacy))
    dst = sqlite3.connect(str(current))
    try:
        _copy_missing(src, dst, "hotel_account", "email")
        _copy_missing(src, dst, "hotel_guest", "email")
        _fill_empty_smtp(src, dst)
        dst.commit()
    finally:
        src.close()
        dst.close()
    _retire(legacy)


def _copy_missing(src: sqlite3.Connection, dst: sqlite3.Connection, table: str, pk: str) -> None:
    if not _has_table(src, table) or not _has_table(dst, table):
        return
    src_cols = {row[1] for row in src.execute(f"PRAGMA table_info({table})")}
    dst_cols = [row[1] for row in dst.execute(f"PRAGMA table_info({table})")]
    cols = [col for col in dst_cols if col in src_cols]
    if not cols:
        return
    existing = {row[0] for row in dst.execute(f"SELECT {pk} FROM {table}")}
    query = f"SELECT {', '.join(cols)} FROM {table}"
    for row in src.execute(query):
        record = dict(zip(cols, row))
        if record[pk] in existing:
            continue
        placeholders = ", ".join("?" for _ in cols)
        dst.execute(
            f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})",
            [record[col] for col in cols],
        )


def _fill_empty_smtp(src: sqlite3.Connection, dst: sqlite3.Connection) -> None:
    if not _has_table(src, "hotel_hotelmeta") or not _has_table(dst, "hotel_hotelmeta"):
        return
    source = src.execute(
        "SELECT smtp_host, smtp_port, smtp_user, smtp_password, smtp_use_ssl FROM hotel_hotelmeta WHERE id = 1"
    ).fetchone()
    dest = dst.execute("SELECT smtp_password FROM hotel_hotelmeta WHERE id = 1").fetchone()
    if not source or not dest:
        return
    if (dest[0] or "").strip() or not (source[3] or "").strip():
        return
    dst.execute(
        """
        UPDATE hotel_hotelmeta
        SET smtp_host = ?, smtp_port = ?, smtp_user = ?, smtp_password = ?, smtp_use_ssl = ?
        WHERE id = 1
        """,
        source,
    )


def _has_table(con: sqlite3.Connection, name: str) -> bool:
    row = con.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (name,)).fetchone()
    return bool(row)


def _retire(legacy: Path) -> None:
    backup = legacy.with_name("somnia_django.db.bak")
    try:
        if backup.exists():
            backup.unlink()
        legacy.replace(backup)
    except OSError:
        pass
