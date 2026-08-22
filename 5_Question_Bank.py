import streamlit as st

from db import fetch_questions, fetch_exams, fetch_authors, delete_question
from utils import inject_style, eyebrow

st.set_page_config(page_title="Question Bank", layout="centered")
inject_style()

eyebrow("Manage")
st.title("Question bank")

try:
    exams = fetch_exams()
    authors = fetch_authors()
except Exception as exc:  # noqa: BLE001
    st.error("Could not connect to the database.")
    st.exception(exc)
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    exam_filter = st.selectbox("Exam", options=["All"] + exams)
with col2:
    author_filter = st.selectbox("Contributor", options=["All"] + authors)
with col3:
    search = st.text_input("Search question text")

questions = fetch_questions(
    exam=None if exam_filter == "All" else exam_filter,
    created_by=None if author_filter == "All" else author_filter,
)

if search.strip():
    needle = search.strip().lower()
    questions = [q for q in questions if needle in q["question"].lower()]

st.caption(f"{len(questions)} question(s)")
st.divider()

if not questions:
    st.info("No questions match these filters.")

for q in questions:
    st.markdown("<div class='qcard'>", unsafe_allow_html=True)
    st.markdown(f"**{q['question']}**")

    for choice in q["choices"]:
        marker = "✓" if choice == q["correct_answer"] else "—"
        st.markdown(f"{marker} {choice}")

    meta_bits = [f"Exam: {q['exam']}", f"Added by: {q['created_by']}"]
    if q.get("slide_deck"):
        meta_bits.append(f"Deck: {q['slide_deck']}")
    if q.get("slide_number"):
        meta_bits.append(f"Slide: {q['slide_number']}")
    st.markdown(f"<div class='qmeta'>{' · '.join(meta_bits)}</div>", unsafe_allow_html=True)

    if st.button("Delete", key=f"delete_{q['id']}"):
        try:
            delete_question(q["id"])
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.error("Could not delete this question.")
            st.exception(exc)

    st.markdown("</div>", unsafe_allow_html=True)
