import streamlit as st

from db import insert_question, fetch_exams
from utils import inject_style, eyebrow

st.set_page_config(page_title="Add Question", layout="centered")
inject_style()

eyebrow("Contribute")
st.title("Add a question")

existing_exams = []
try:
    existing_exams = fetch_exams()
except Exception:  # noqa: BLE001
    pass

with st.form("add_question_form", clear_on_submit=True):
    question = st.text_area("Question", placeholder="What is the time complexity of binary search?", height=100)

    st.markdown("**Answer choices**")
    st.caption("Leave a row blank if the question has fewer than four choices.")
    c1 = st.text_input("Choice 1")
    c2 = st.text_input("Choice 2")
    c3 = st.text_input("Choice 3")
    c4 = st.text_input("Choice 4")

    choice_list = [c.strip() for c in [c1, c2, c3, c4] if c.strip()]
    correct_answer = st.selectbox(
        "Correct answer",
        options=choice_list if choice_list else ["Enter choices above first"],
    )

    st.markdown("**Details**")
    col1, col2 = st.columns(2)
    with col1:
        exam_choice = st.selectbox(
            "Exam",
            options=["New exam..."] + existing_exams,
            help="Pick an existing exam or add a new one.",
        )
        exam_new = ""
        if exam_choice == "New exam...":
            exam_new = st.text_input("New exam name")
        created_by = st.text_input("Your name / username")
    with col2:
        slide_deck = st.text_input("Slide deck (optional)")
        slide_number = st.number_input("Slide number (optional)", min_value=0, step=1, value=0)

    submitted = st.form_submit_button("Add question", use_container_width=True)

    if submitted:
        exam = exam_new.strip() if exam_choice == "New exam..." else exam_choice
        errors = []
        if not question.strip():
            errors.append("Question text is required.")
        if len(choice_list) < 2:
            errors.append("At least two answer choices are required.")
        if not correct_answer or correct_answer not in choice_list:
            errors.append("Select a valid correct answer.")
        if not exam:
            errors.append("Exam name is required.")
        if not created_by.strip():
            errors.append("Your name is required.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            record = {
                "question": question.strip(),
                "choices": choice_list,
                "correct_answer": correct_answer,
                "created_by": created_by.strip(),
                "exam": exam,
                "slide_deck": slide_deck.strip() or None,
                "slide_number": int(slide_number) if slide_number else None,
            }
            try:
                insert_question(record)
                st.success("Question added to the bank.")
            except Exception as exc:  # noqa: BLE001
                st.error("Could not save the question.")
                st.exception(exc)
