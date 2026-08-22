"""
utils.py

Shared visual styling (the "sophisticated, emoji-free" look) and the
parsing / validation logic used by the bulk upload page.
"""

from __future__ import annotations

import io
import json
from typing import Any

import pandas as pd
import streamlit as st

REQUIRED_FIELDS = ["question", "choices", "correct_answer", "created_by", "exam"]
OPTIONAL_FIELDS = ["slide_deck", "slide_number"]
ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS


# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------

def inject_style() -> None:
    """Injects the shared typography / color system used on every page.

    Palette
        ink      #1C2126   primary text / headings
        paper    #F6F4EF   page background
        panel    #FFFFFF   card background
        slate    #5B6470   secondary text
        rule     #DCD8CE   hairline borders / dividers
        brass    #9C7A3C   accent (selection, active states)
        pine     #3F6656   correct / success
        clay     #A24C3D   incorrect / error

    Type
        display  "Fraunces"      headings, question stems
        body     "Source Sans 3" UI text, choices, body copy
        mono     "IBM Plex Mono" timers, counters, question numbers
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Source+Sans+3:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

        :root {
            --ink: #1C2126;
            --paper: #F6F4EF;
            --panel: #FFFFFF;
            --slate: #5B6470;
            --rule: #DCD8CE;
            --brass: #9C7A3C;
            --pine: #3F6656;
            --clay: #A24C3D;
        }

        html, body, [class*="css"] {
            font-family: 'Source Sans 3', sans-serif;
            color: var(--ink);
        }

        .stApp {
            background-color: var(--paper);
        }

        h1, h2, h3, h4 {
            font-family: 'Fraunces', serif;
            font-weight: 600;
            letter-spacing: -0.01em;
            color: var(--ink);
        }

        h1 {
            border-bottom: 1px solid var(--rule);
            padding-bottom: 0.5rem;
            margin-bottom: 1.25rem;
        }

        [data-testid="stSidebar"] {
            background-color: var(--panel);
            border-right: 1px solid var(--rule);
        }

        [data-testid="stSidebar"] * {
            font-family: 'Source Sans 3', sans-serif;
        }

        .eyebrow {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--brass);
            margin-bottom: 0.25rem;
        }

        .qcard {
            background-color: var(--panel);
            border: 1px solid var(--rule);
            border-left: 3px solid var(--brass);
            padding: 1.5rem 1.75rem;
            margin-bottom: 1rem;
        }

        .qmeta {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            color: var(--slate);
        }

        .stButton>button, .stDownloadButton>button {
            font-family: 'Source Sans 3', sans-serif;
            background-color: var(--ink);
            color: var(--paper);
            border: 1px solid var(--ink);
            border-radius: 2px;
            padding: 0.5rem 1.25rem;
            font-weight: 500;
        }

        .stButton>button:hover, .stDownloadButton>button:hover {
            background-color: var(--brass);
            border-color: var(--brass);
            color: var(--paper);
        }

        .stButton>button[kind="secondary"] {
            background-color: transparent;
            color: var(--ink);
        }

        div[data-testid="stMetricValue"] {
            font-family: 'Fraunces', serif;
            color: var(--ink);
        }

        div[data-baseweb="tab-list"] {
            border-bottom: 1px solid var(--rule);
        }

        hr {
            border-color: var(--rule);
        }

        .timer-chip {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1.1rem;
            border: 1px solid var(--rule);
            padding: 0.35rem 0.9rem;
            display: inline-block;
            background-color: var(--panel);
        }

        .timer-chip.low {
            border-color: var(--clay);
            color: var(--clay);
        }

        .result-correct {
            color: var(--pine);
            font-weight: 600;
        }

        .result-incorrect {
            color: var(--clay);
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def eyebrow(text: str) -> None:
    """Small uppercase monospace label used above page titles."""
    st.markdown(f"<div class='eyebrow'>{text}</div>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Bulk upload parsing
# --------------------------------------------------------------------------

def bulk_template_csv() -> bytes:
    df = pd.DataFrame(
        [
            {
                "question": "What is the time complexity of binary search?",
                "choices": "O(n) | O(log n) | O(n log n) | O(1)",
                "correct_answer": "O(log n)",
                "created_by": "jane.doe",
                "exam": "Data Structures Midterm",
                "slide_deck": "Week 4 - Searching",
                "slide_number": 12,
            }
        ]
    )
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def bulk_template_json() -> bytes:
    sample = [
        {
            "question": "What is the time complexity of binary search?",
            "choices": ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
            "correct_answer": "O(log n)",
            "created_by": "jane.doe",
            "exam": "Data Structures Midterm",
            "slide_deck": "Week 4 - Searching",
            "slide_number": 12,
        }
    ]
    return json.dumps(sample, indent=2).encode("utf-8")


def _split_choices(raw: Any) -> list[str]:
    """Choices may arrive as a real list (JSON) or a delimited string (CSV)."""
    if isinstance(raw, list):
        return [str(c).strip() for c in raw if str(c).strip()]
    if pd.isna(raw):
        return []
    text = str(raw)
    for delim in ["|", ";", "\n"]:
        if delim in text:
            return [c.strip() for c in text.split(delim) if c.strip()]
    return [text.strip()] if text.strip() else []


def parse_upload(file) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse an uploaded CSV or JSON file into normalized question records.

    Returns (records, errors). Records that fail validation are excluded
    from the returned list and instead described in `errors`.
    """
    name = file.name.lower()
    raw_rows: list[dict[str, Any]] = []

    if name.endswith(".json"):
        try:
            data = json.loads(file.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            return [], [f"Could not parse JSON file: {exc}"]
        if isinstance(data, dict):
            data = [data]
        raw_rows = data
    elif name.endswith(".csv"):
        try:
            df = pd.read_csv(file)
        except Exception as exc:  # noqa: BLE001
            return [], [f"Could not parse CSV file: {exc}"]
        raw_rows = df.to_dict(orient="records")
    else:
        return [], ["Unsupported file type. Please upload a .csv or .json file."]

    records: list[dict[str, Any]] = []
    errors: list[str] = []

    for i, row in enumerate(raw_rows, start=1):
        row_errors = []

        question = str(row.get("question", "")).strip()
        if not question or question.lower() == "nan":
            row_errors.append("missing question text")

        choices = _split_choices(row.get("choices"))
        if len(choices) < 2:
            row_errors.append("fewer than 2 answer choices")

        correct = str(row.get("correct_answer", "")).strip()
        if not correct or correct.lower() == "nan":
            row_errors.append("missing correct_answer")
        elif choices and correct not in choices:
            row_errors.append("correct_answer does not match any listed choice")

        created_by = str(row.get("created_by", "")).strip()
        if not created_by or created_by.lower() == "nan":
            row_errors.append("missing created_by")

        exam = str(row.get("exam", "")).strip()
        if not exam or exam.lower() == "nan":
            row_errors.append("missing exam")

        if row_errors:
            errors.append(f"Row {i}: {', '.join(row_errors)}")
            continue

        slide_deck = row.get("slide_deck")
        slide_deck = str(slide_deck).strip() if pd.notna(slide_deck) and str(slide_deck).strip().lower() != "nan" else None

        slide_number = row.get("slide_number")
        try:
            slide_number = int(slide_number) if pd.notna(slide_number) and str(slide_number).strip() != "" else None
        except (ValueError, TypeError):
            slide_number = None

        records.append(
            {
                "question": question,
                "choices": choices,
                "correct_answer": correct,
                "created_by": created_by,
                "exam": exam,
                "slide_deck": slide_deck,
                "slide_number": slide_number,
            }
        )

    return records, errors
