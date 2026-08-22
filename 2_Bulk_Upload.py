import pandas as pd
import streamlit as st

from db import bulk_insert_questions
from utils import inject_style, eyebrow, bulk_template_csv, bulk_template_json, parse_upload

st.set_page_config(page_title="Bulk Upload", layout="centered")
inject_style()

eyebrow("Contribute")
st.title("Bulk upload questions")

st.write(
    "Upload a CSV or JSON file of questions — handy when you've generated "
    "a batch with an LLM. Each row needs a question, at least two choices, "
    "a correct answer, the contributor's name, and the exam it belongs to. "
    "Slide deck and slide number are optional."
)

with st.expander("Column reference and templates"):
    st.markdown(
        """
        | Field | Required | Notes |
        |---|---|---|
        | `question` | yes | The question text |
        | `choices` | yes | JSON: a list of strings. CSV: separate choices with `\\|` |
        | `correct_answer` | yes | Must exactly match one of the choices |
        | `created_by` | yes | Name or username of the contributor |
        | `exam` | yes | The exam this question belongs to |
        | `slide_deck` | no | Source slide deck |
        | `slide_number` | no | Source slide number |
        """
    )
    col1, col2 = st.columns(2)
    col1.download_button(
        "Download CSV template",
        data=bulk_template_csv(),
        file_name="question_upload_template.csv",
        mime="text/csv",
        use_container_width=True,
    )
    col2.download_button(
        "Download JSON template",
        data=bulk_template_json(),
        file_name="question_upload_template.json",
        mime="application/json",
        use_container_width=True,
    )

st.divider()

uploaded = st.file_uploader("Upload file", type=["csv", "json"])

if uploaded is not None:
    records, errors = parse_upload(uploaded)

    if records:
        st.subheader(f"{len(records)} question(s) ready to import")
        preview_df = pd.DataFrame(records)
        st.dataframe(preview_df, use_container_width=True, hide_index=True)

    if errors:
        st.subheader(f"{len(errors)} row(s) could not be imported")
        for e in errors:
            st.warning(e)

    if records:
        if st.button(f"Import {len(records)} question(s)", use_container_width=True):
            try:
                inserted = bulk_insert_questions(records)
                st.success(f"Imported {inserted} question(s) into the bank.")
            except Exception as exc:  # noqa: BLE001
                st.error("Import failed.")
                st.exception(exc)
    elif not errors:
        st.info("The file didn't contain any rows.")
