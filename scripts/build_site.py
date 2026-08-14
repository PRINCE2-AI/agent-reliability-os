from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.demo_agent import run_demo_suite


def main() -> None:
    result = run_demo_suite(".data/site_demo.sqlite3")
    summary = result["summary"]
    rows = "\n".join(
        f"""
        <tr>
          <td>{run['mode']}</td>
          <td>{run['scenario']}</td>
          <td>{run['status']}</td>
          <td>{run['evaluation']['task_success']}</td>
          <td>{run['evaluation']['tool_misuse_risk']}</td>
          <td>{run['evaluation']['policy_coverage']}</td>
        </tr>
        """
        for run in result["runs"]
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Agent Reliability OS</title>
  <style>
    :root {{ color-scheme: light; --ink:#17202a; --muted:#5f6b7a; --line:#d8dee8; --bg:#f7f9fc; --accent:#0b7285; --risk:#b42318; --ok:#0f766e; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; color:var(--ink); background:var(--bg); }}
    header {{ padding:56px 7vw 28px; background:#ffffff; border-bottom:1px solid var(--line); }}
    h1 {{ margin:0; font-size:42px; line-height:1.05; letter-spacing:0; }}
    .subtitle {{ margin-top:14px; max-width:880px; color:var(--muted); font-size:18px; }}
    main {{ padding:28px 7vw 56px; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin:20px 0 28px; }}
    .metric {{ background:#fff; border:1px solid var(--line); border-radius:8px; padding:18px; }}
    .metric strong {{ display:block; font-size:30px; margin-bottom:6px; }}
    .metric span {{ color:var(--muted); font-size:14px; }}
    section {{ margin-top:28px; }}
    table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line); border-radius:8px; overflow:hidden; }}
    th, td {{ padding:12px 14px; border-bottom:1px solid var(--line); text-align:left; font-size:14px; }}
    th {{ background:#eef3f7; }}
    code, pre {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
    pre {{ background:#101828; color:#f8fafc; padding:16px; overflow:auto; border-radius:8px; }}
    .links a {{ display:inline-block; margin:0 12px 10px 0; color:var(--accent); font-weight:600; }}
    @media (max-width:800px) {{ .grid {{ grid-template-columns:1fr 1fr; }} h1 {{ font-size:34px; }} }}
    @media (max-width:520px) {{ .grid {{ grid-template-columns:1fr; }} table {{ display:block; overflow-x:auto; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Agent Reliability OS</h1>
    <p class="subtitle">A production-style observability, evaluation, and runtime policy control plane for tool-using LLM agents. It traces every step, scores reliability, detects risky tool use, and compares baseline agents against governed agents.</p>
    <p class="links">
      <a href="https://github.com/PRINCE2-AI/agent-reliability-os">GitHub Repository</a>
      <a href="https://github.com/PRINCE2-AI/agent-reliability-os/actions">CI Proof</a>
      <a href="./sample_outputs.json">Sample Outputs</a>
    </p>
  </header>
  <main>
    <div class="grid">
      <div class="metric"><strong>{summary['total_runs']}</strong><span>benchmark runs</span></div>
      <div class="metric"><strong>{summary['baseline_risky_successes']}</strong><span>baseline risky successes</span></div>
      <div class="metric"><strong>{summary['protected_blocks']}</strong><span>protected blocks</span></div>
      <div class="metric"><strong>{summary['avg_protected_policy_coverage']}</strong><span>protected policy coverage</span></div>
    </div>
    <section>
      <h2>Benchmark Results</h2>
      <table>
        <thead><tr><th>Mode</th><th>Scenario</th><th>Status</th><th>Task Success</th><th>Tool Misuse Risk</th><th>Policy Coverage</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    <section>
      <h2>What This Proves</h2>
      <pre>{json.dumps(summary, indent=2)}</pre>
    </section>
  </main>
</body>
</html>
"""
    site = Path("site")
    site.mkdir(exist_ok=True)
    site.joinpath("index.html").write_text(html, encoding="utf-8")
    site.joinpath("sample_outputs.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("Built site/index.html")


if __name__ == "__main__":
    main()
