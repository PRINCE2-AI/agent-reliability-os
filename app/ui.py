from __future__ import annotations

try:
    import streamlit as st
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Install requirements.txt to run the Streamlit dashboard.") from exc

from app.config import load_settings
from app.demo_agent import SCENARIOS, DemoAgent, run_demo_suite
from app.trace_store import TraceStore

settings = load_settings()
store = TraceStore(settings.trace_db_path)

st.set_page_config(page_title="Agent Reliability OS", layout="wide")
st.title("Agent Reliability OS")
st.caption("Trace, evaluate, and govern tool-using LLM agents.")

mode = st.sidebar.selectbox("Mode", ["protected", "baseline"])
scenario_name = st.sidebar.selectbox("Scenario", [scenario.name for scenario in SCENARIOS])

if st.sidebar.button("Run Scenario"):
    scenario = next(item for item in SCENARIOS if item.name == scenario_name)
    result = DemoAgent(store).run(scenario, mode=mode)
    st.session_state["latest"] = result

if st.sidebar.button("Run Benchmark Suite"):
    st.session_state["suite"] = run_demo_suite(settings.trace_db_path)

latest = st.session_state.get("latest")
if latest:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", latest["status"])
    c2.metric("Task Success", latest["evaluation"]["task_success"])
    c3.metric("Tool Misuse Risk", latest["evaluation"]["tool_misuse_risk"])
    c4.metric("Policy Coverage", latest["evaluation"]["policy_coverage"])
    st.subheader("Final Answer")
    st.write(latest["final_answer"])
    st.subheader("Trace")
    st.json(latest["events"])

suite = st.session_state.get("suite")
if suite:
    st.subheader("Benchmark Summary")
    st.json(suite["summary"])
    st.subheader("Runs")
    st.dataframe(
        [
            {
                "mode": run["mode"],
                "scenario": run["scenario"],
                "status": run["status"],
                "task_success": run["evaluation"]["task_success"],
                "tool_misuse_risk": run["evaluation"]["tool_misuse_risk"],
                "policy_coverage": run["evaluation"]["policy_coverage"],
            }
            for run in suite["runs"]
        ],
        use_container_width=True,
    )

