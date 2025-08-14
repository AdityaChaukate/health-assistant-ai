
# streamlit_app.py
# Simple GUI to explore the Health Assistant rule base.

import streamlit as st

from typing import List, Set, Tuple

Rule = Tuple[Set[str], str, str]

RULES: List[Rule] = [
    ({"fever", "cough", "body_ache"}, "flu_suspected", "Fever + cough + body ache ⇒ Flu suspected"),
    ({"runny_nose", "sneezing", "no_fever"}, "common_cold", "Runny nose + sneezing + no fever ⇒ Common cold"),
    ({"itchy_eyes", "sneezing", "runny_nose"}, "allergy", "Itchy eyes + sneezing + runny nose ⇒ Allergy"),
    ({"dry_cough", "fever", "loss_of_smell"}, "covid_suspected", "Dry cough + fever + loss of smell ⇒ COVID suspected"),
    ({"covid_suspected"}, "recommend_test", "If COVID suspected ⇒ Recommend COVID test"),
    ({"flu_suspected"}, "recommend_paracetamol", "If Flu suspected ⇒ Recommend paracetamol"),
    ({"flu_suspected"}, "see_doctor_if_persistent", "If Flu suspected ⇒ See doctor if symptoms persist"),
    ({"common_cold"}, "recommend_home_remedies", "If Common cold ⇒ Recommend home remedies"),
    ({"sore_throat", "mild_fever"}, "throat_infection", "Sore throat + mild fever ⇒ Throat infection"),
    ({"throat_infection"}, "recommend_warm_salts_gargle", "Throat infection ⇒ Warm salt-water gargle"),
]

ALL_FACTS = sorted({f for r in RULES for f in list(r[0]) + [r[1]]})

def forward_chain(initial_facts: Set[str], rules: List[Rule]):
    known = set(initial_facts)
    trace = []
    changed = True
    while changed:
        changed = False
        for conds, concl, note in rules:
            if conds.issubset(known) and concl not in known:
                trace.append((conds, concl, note))
                known.add(concl)
                changed = True
    return known, trace

st.set_page_config(page_title="Health Assistant (Forward/Backward Chaining)", page_icon="🧠")

st.title("🧠 Health Assistant — Rule-Based Reasoning")
st.write("Toggle symptoms/signals, then run **Forward Chaining**.")

with st.expander("Select initial facts (symptoms/signals)"):
    selections = set()
    for f in sorted({f for r in RULES for f in r[0]}):
        if st.checkbox(f):
            selections.add(f)

if st.button("Run Forward Chaining"):
    final, trace = forward_chain(selections, RULES)
    st.subheader("Forward Chaining Trace")
    for i, (conds, concl, note) in enumerate(trace, 1):
        st.write(f"**Step {i}**: {note} → add `{concl}`")
    st.subheader("Final Inferred Facts")
    inferred = sorted(final - selections)
    if inferred:
        for f in inferred:
            st.write(f"- {f}")
    else:
        st.info("No new facts inferred.")

st.divider()
st.subheader("Backward Chaining (simple)")
st.write("Pick a goal and the app will check if it can be concluded from the selected facts using the rules.")

goal = st.selectbox("Select goal", sorted({r[1] for r in RULES}))
if st.button("Try to prove goal"):
    # Simple recursive prover
    def backward_chain(goal, facts, rules, visited=None):
        if visited is None:
            visited = set()
        if goal in facts:
            return True, [f"'{goal}' is already known."]
        if goal in visited:
            return False, [f"Cycle on '{goal}' avoided."]
        visited.add(goal)
        applicable = [r for r in rules if r[1] == goal]
        steps = []
        if not applicable:
            return False, [f"No rules conclude '{goal}'."]
        for conds, concl, note in applicable:
            steps.append(f"Trying rule: {note}")
            ok_all = True
            for c in conds:
                ok, sub = backward_chain(c, facts, rules, visited)
                steps += sub
                if not ok:
                    steps.append(f"Failed to prove '{c}'.")
                    ok_all = False
                    break
            if ok_all:
                steps.append(f"Proved goal '{goal}'.")
                return True, steps
        steps.append(f"Could not prove '{goal}'.")
        return False, steps

    ok, steps = backward_chain(goal, selections, RULES)
    st.write("\n".join(f"- {s}" for s in steps))
    st.success("Goal PROVED ✅" if ok else "Goal NOT proved ❌")
