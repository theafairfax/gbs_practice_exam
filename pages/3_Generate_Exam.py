import streamlit as st

from db import fetch_exams, fetch_slide_decks, count_questions, fetch_random_questions
from utils import inject_style, eyebrow

st.set_page_config(page_title="Generate Exam", layout="centered")
inject_style()

eyebrow("Practice")
st.title("Generate a practice exam")

try:
    exams = fetch_exams()
except Exception as exc:  # noqa: BLE001
    st.error("Could not connect to the database.")
    st.exception(exc)
    st.stop()

if not exams:
    st.info("No questions have been added yet. Add some on the **Add Question** page first.")
    st.stop()

exam = st.selectbox("Exam material", options=exams)

decks = fetch_slide_decks(exam=exam)
selected_decks = []
if decks:
    selected_decks = st.multiselect(
        "Limit to specific slide decks (optional)",
        options=decks,
        help="Leave empty to draw from every slide deck under this exam.",
    )

available = count_questions(exam=exam)
if selected_decks:
    available = sum(count_questions(exam=exam, slide_deck=d) for d in selected_decks)

st.caption(f"{available} question(s) available with the current filters.")

col1, col2 = st.columns(2)
with col1:
    num_questions = st.number_input(
        "Number of questions",
        min_value=1,
        max_value=max(available, 1),
        value=min(10, max(available, 1)),
        step=1,
    )
with col2:
    time_limit = st.number_input(
        "Time limit per question (seconds)",
        min_value=10,
        max_value=1800,
        value=60,
        step=10,
    )

shuffle_choices = st.checkbox("Shuffle answer choices", value=True)

st.divider()

start = st.button("Start exam", use_container_width=True, disabled=available == 0)

if start:
    questions = fetch_random_questions(exam=exam, n=int(num_questions), slide_decks=selected_decks or None)
    if not questions:
        st.error("No questions matched these filters.")
    else:
        st.session_state["exam_config"] = {
            "exam": exam,
            "slide_decks": selected_decks,
            "time_limit": int(time_limit),
            "shuffle_choices": shuffle_choices,
        }
        st.session_state["exam_questions"] = questions
        st.session_state["exam_index"] = 0
        st.session_state["exam_answers"] = {}
        st.session_state["exam_question_start"] = None
        st.session_state["exam_finished"] = False
        st.switch_page("pages/4_Take_Exam.py")
