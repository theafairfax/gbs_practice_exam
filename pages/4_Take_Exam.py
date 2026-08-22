import random
import time

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from utils import inject_style, eyebrow

st.set_page_config(page_title="Take Exam", layout="centered")
inject_style()

if "exam_questions" not in st.session_state or not st.session_state["exam_questions"]:
    st.info("No practice exam is in progress.")
    if st.button("Go to Generate Exam"):
        st.switch_page("pages/3_Generate_Exam.py")
    st.stop()

config = st.session_state["exam_config"]
questions = st.session_state["exam_questions"]
index = st.session_state["exam_index"]
answers = st.session_state["exam_answers"]
time_limit = config["time_limit"]

# ---------------------------------------------------------------------
# Results view
# ---------------------------------------------------------------------
if st.session_state.get("exam_finished"):
    eyebrow(config["exam"])
    st.title("Results")

    correct_count = sum(1 for a in answers.values() if a["is_correct"])
    total = len(questions)
    st.metric("Score", f"{correct_count} / {total}")

    st.divider()

    for i, q in enumerate(questions):
        a = answers.get(i, {"selected": None, "is_correct": False, "timed_out": False})
        st.markdown(f"<div class='qcard'>", unsafe_allow_html=True)
        st.markdown(f"<div class='qmeta'>Question {i + 1}</div>", unsafe_allow_html=True)
        st.markdown(f"**{q['question']}**")
        status = "result-correct" if a["is_correct"] else "result-incorrect"
        your_answer = a["selected"] if a["selected"] else ("No answer (time expired)" if a["timed_out"] else "No answer")
        st.markdown(f"<span class='{status}'>Your answer: {your_answer}</span>", unsafe_allow_html=True)
        if not a["is_correct"]:
            st.markdown(f"Correct answer: **{q['correct_answer']}**")
        meta_bits = [f"Exam: {q['exam']}"]
        if q.get("slide_deck"):
            meta_bits.append(f"Deck: {q['slide_deck']}")
        if q.get("slide_number"):
            meta_bits.append(f"Slide: {q['slide_number']}")
        st.markdown(f"<div class='qmeta'>{' · '.join(meta_bits)}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("New exam", use_container_width=True):
        for key in ["exam_config", "exam_questions", "exam_index", "exam_answers", "exam_question_start", "exam_finished", "exam_choice_order"]:
            st.session_state.pop(key, None)
        st.switch_page("pages/3_Generate_Exam.py")
    if col2.button("Back to home", use_container_width=True):
        st.switch_page("app.py")
    st.stop()

# ---------------------------------------------------------------------
# In-progress exam view
# ---------------------------------------------------------------------
st_autorefresh(interval=1000, key="exam_timer_refresh")

q = questions[index]

if st.session_state.get("exam_question_start") is None:
    st.session_state["exam_question_start"] = time.time()

# Stable, per-question shuffled choice order
order_map = st.session_state.setdefault("exam_choice_order", {})
if index not in order_map:
    choices = list(q["choices"])
    if config.get("shuffle_choices", True):
        random.shuffle(choices)
    order_map[index] = choices
choices = order_map[index]

elapsed = time.time() - st.session_state["exam_question_start"]
remaining = max(0, time_limit - elapsed)

eyebrow(f"{config['exam']} · Question {index + 1} of {len(questions)}")
st.title("Practice exam")

st.progress(index / len(questions))

timer_class = "timer-chip low" if remaining <= 10 else "timer-chip"
st.markdown(f"<div class='{timer_class}'>{int(remaining):02d}s remaining</div>", unsafe_allow_html=True)

st.markdown("<div class='qcard'>", unsafe_allow_html=True)
st.markdown(f"**{q['question']}**")
st.markdown("</div>", unsafe_allow_html=True)

selection_key = f"selection_{index}"
selected = st.radio(
    "Select an answer",
    options=choices,
    index=None,
    key=selection_key,
    label_visibility="collapsed",
)

time_expired = remaining <= 0
if time_expired:
    st.warning("Time's up for this question.")

button_label = "Finish exam" if index == len(questions) - 1 else "Submit & next"
advance = st.button(button_label, use_container_width=True, disabled=False)

if advance or time_expired:
    if index not in answers:
        is_correct = selected == q["correct_answer"]
        answers[index] = {
            "selected": selected,
            "is_correct": is_correct,
            "timed_out": time_expired and selected is None,
        }
        st.session_state["exam_answers"] = answers

    if index + 1 < len(questions):
        st.session_state["exam_index"] = index + 1
        st.session_state["exam_question_start"] = None
    else:
        st.session_state["exam_finished"] = True
    st.rerun()
