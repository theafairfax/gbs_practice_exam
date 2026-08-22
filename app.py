import streamlit as st

from db import fetch_exams, fetch_authors, count_questions
from utils import inject_style, eyebrow

st.set_page_config(
    page_title="Practice Exam Bank",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="expanded",
)

inject_style()

eyebrow("Practice Exam Bank")
st.title("A shared question bank for exam prep")

st.write(
    "Contribute questions, pull them together into timed practice exams, "
    "and keep a running bank of material by course and slide deck. "
    "Use the pages in the left sidebar to add questions, upload in bulk, "
    "or generate a practice exam."
)

st.divider()

try:
    total = count_questions()
    exams = fetch_exams()
    authors = fetch_authors()

    col1, col2, col3 = st.columns(3)
    col1.metric("Questions in bank", total)
    col2.metric("Exams covered", len(exams))
    col3.metric("Contributors", len(authors))

    if exams:
        st.subheader("Exams currently in the bank")
        for exam in exams:
            st.markdown(f"— {exam}  ·  {count_questions(exam=exam)} questions")
    else:
        st.info("No questions have been added yet. Start on the **Add Question** page.")

except Exception as exc:  # noqa: BLE001
    st.error(
        "Could not connect to the Supabase database. Check that `SUPABASE_URL` "
        "and `SUPABASE_KEY` are set correctly in your Streamlit secrets."
    )
    st.exception(exc)

st.divider()

st.markdown(
    """
    **How it works**

    1. **Add Question** — enter a single question, its choices, the correct
       answer, and which exam it belongs to.
    2. **Bulk Upload** — upload a CSV or JSON file of questions at once,
       useful when questions were generated with an LLM.
    3. **Generate Exam** — choose an exam, how many questions, and a time
       limit per question, then sit the practice exam.
    4. **Question Bank** — browse, search, and manage everything that has
       been contributed.
    """
)
