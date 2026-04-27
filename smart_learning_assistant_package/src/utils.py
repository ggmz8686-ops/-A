import csv
import json
import os
import re
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Optional

from .config import DB_PATH


def read_jsonl(file_path: str) -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = []
    if not os.path.exists(file_path):
        return data

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return data


def write_jsonl(file_path: str, data: list[dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        for item in data:
            json.dump(item, file, ensure_ascii=False)
            file.write("\n")


def read_csv(file_path: str) -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = []
    if not os.path.exists(file_path):
        return data

    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data


def write_csv(file_path: str, data: list[dict[str, Any]], fieldnames: list[str]) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def _ensure_column(cursor: sqlite3.Cursor, table_name: str, column_name: str, ddl: str) -> None:
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if column_name not in existing_columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {ddl}")


def init_database() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal TEXT,
            start_date TEXT,
            end_date TEXT,
            subjects TEXT,
            created_at TEXT,
            study_hours_per_day REAL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER,
            task_name TEXT,
            subject TEXT,
            duration INTEGER,
            status TEXT,
            scheduled_date TEXT,
            completed_at TEXT,
            FOREIGN KEY (plan_id) REFERENCES study_plans (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS wrong_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            user_answer TEXT,
            correct_answer TEXT,
            subject TEXT,
            difficulty TEXT,
            grade TEXT,
            question_type TEXT,
            timestamp TEXT,
            notebook_status TEXT DEFAULT 'active',
            review_count INTEGER DEFAULT 0,
            last_reviewed_at TEXT,
            mastered_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vocab_learning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT,
            meaning TEXT,
            example TEXT,
            last_review TEXT,
            next_review TEXT,
            review_count INTEGER,
            difficulty INTEGER
        )
        """
    )

    _ensure_column(cursor, "wrong_questions", "grade", "grade TEXT")
    _ensure_column(cursor, "wrong_questions", "notebook_status", "notebook_status TEXT DEFAULT 'active'")
    _ensure_column(cursor, "wrong_questions", "review_count", "review_count INTEGER DEFAULT 0")
    _ensure_column(cursor, "wrong_questions", "last_reviewed_at", "last_reviewed_at TEXT")
    _ensure_column(cursor, "wrong_questions", "mastered_at", "mastered_at TEXT")
    _ensure_column(cursor, "study_plans", "study_hours_per_day", "study_hours_per_day REAL")

    conn.commit()
    conn.close()


def get_db_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def calculate_next_review_date(current_date: str, interval: int) -> str:
    date_obj = datetime.strptime(current_date, "%Y-%m-%d")
    next_date = date_obj + timedelta(days=interval)
    return next_date.strftime("%Y-%m-%d")


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_text(text: str) -> str:
    lowered = clean_text(text).lower()
    lowered = lowered.replace("，", ",").replace("。", ".").replace("：", ":").replace("；", ";")
    lowered = lowered.replace("（", "(").replace("）", ")").replace("“", '"').replace("”", '"')
    return lowered


def format_time(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    parts: list[str] = []
    if hours:
        parts.append(f"{hours}小时")
    if minutes:
        parts.append(f"{minutes}分钟")
    if remaining_seconds:
        parts.append(f"{remaining_seconds}秒")
    return " ".join(parts) if parts else "0秒"


def get_current_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_current_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_input(text: Optional[str], min_length: int = 1, max_length: Optional[int] = None) -> bool:
    if text is None:
        return False
    trimmed = text.strip()
    if len(trimmed) < min_length:
        return False
    if max_length is not None and len(trimmed) > max_length:
        return False
    return True


def split_text_into_chunks(text: str, chunk_size: int = 500) -> list[str]:
    return [text[index:index + chunk_size] for index in range(0, len(text), chunk_size)]


def calculate_similarity(text1: str, text2: str) -> float:
    normalized1 = normalize_text(text1)
    normalized2 = normalize_text(text2)

    if not normalized1 and not normalized2:
        return 1.0
    if not normalized1 or not normalized2:
        return 0.0

    if " " in normalized1 or " " in normalized2:
        units1 = set(normalized1.split())
        units2 = set(normalized2.split())
    else:
        units1 = {normalized1[index:index + 2] for index in range(max(len(normalized1) - 1, 1))}
        units2 = {normalized2[index:index + 2] for index in range(max(len(normalized2) - 1, 1))}
        if len(normalized1) == 1:
            units1 = {normalized1}
        if len(normalized2) == 1:
            units2 = {normalized2}

    if not units1 and not units2:
        return 1.0
    union = units1.union(units2)
    if not union:
        return 0.0
    return len(units1.intersection(units2)) / len(union)
