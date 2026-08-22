"""
db.py

Thin data-access layer around Supabase. Every function in this module
returns plain Python objects (lists / dicts) so the Streamlit pages never
touch the Supabase client directly.
"""

from __future__ import annotations

import random
from typing import Any

import streamlit as st
from supabase import create_client, Client

TABLE = "questions"


@st.cache_resource(show_spinner=False)
def get_client() -> Client:
    """Create (once) and cache the Supabase client for this session."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def _client() -> Client:
    return get_client()


# --------------------------------------------------------------------------
# Writes
# --------------------------------------------------------------------------

def insert_question(record: dict[str, Any]) -> dict[str, Any]:
    """Insert a single question. Returns the inserted row."""
    resp = _client().table(TABLE).insert(record).execute()
    return resp.data[0] if resp.data else {}


def bulk_insert_questions(records: list[dict[str, Any]]) -> int:
    """Insert many questions at once. Returns the number of rows inserted."""
    if not records:
        return 0
    resp = _client().table(TABLE).insert(records).execute()
    return len(resp.data) if resp.data else 0


def delete_question(question_id: str) -> None:
    _client().table(TABLE).delete().eq("id", question_id).execute()


def update_question(question_id: str, record: dict[str, Any]) -> None:
    _client().table(TABLE).update(record).eq("id", question_id).execute()


# --------------------------------------------------------------------------
# Reads
# --------------------------------------------------------------------------

def fetch_questions(
    exam: str | None = None,
    slide_deck: str | None = None,
    created_by: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    query = _client().table(TABLE).select("*")
    if exam:
        query = query.eq("exam", exam)
    if slide_deck:
        query = query.eq("slide_deck", slide_deck)
    if created_by:
        query = query.eq("created_by", created_by)
    query = query.order("created_at", desc=True)
    if limit:
        query = query.limit(limit)
    resp = query.execute()
    return resp.data or []


def fetch_distinct(column: str) -> list[str]:
    """Return the sorted, distinct, non-null values of a column."""
    resp = _client().table(TABLE).select(column).execute()
    values = {row[column] for row in (resp.data or []) if row.get(column)}
    return sorted(values)


def fetch_exams() -> list[str]:
    return fetch_distinct("exam")


def fetch_authors() -> list[str]:
    return fetch_distinct("created_by")


def fetch_slide_decks(exam: str | None = None) -> list[str]:
    query = _client().table(TABLE).select("slide_deck")
    if exam:
        query = query.eq("exam", exam)
    resp = query.execute()
    values = {row["slide_deck"] for row in (resp.data or []) if row.get("slide_deck")}
    return sorted(values)


def count_questions(exam: str | None = None, slide_deck: str | None = None) -> int:
    query = _client().table(TABLE).select("id", count="exact")
    if exam:
        query = query.eq("exam", exam)
    if slide_deck:
        query = query.eq("slide_deck", slide_deck)
    resp = query.execute()
    return resp.count or 0


def fetch_random_questions(
    exam: str,
    n: int,
    slide_decks: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Pull a random sample of n questions for the given exam, optionally
    restricted to a set of slide decks. Sampling is done client-side since
    the free Supabase tier's PostgREST endpoint has no simple RANDOM() hook.
    """
    query = _client().table(TABLE).select("*").eq("exam", exam)
    if slide_decks:
        query = query.in_("slide_deck", slide_decks)
    resp = query.execute()
    pool = resp.data or []
    random.shuffle(pool)
    return pool[:n]
