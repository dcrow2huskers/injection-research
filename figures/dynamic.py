import os
import re
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Optional: for Sankey
try:
    import plotly.graph_objects as go
    HAVE_PLOTLY = True
except ImportError:
    HAVE_PLOTLY = False
    print("plotly not installed; Sankey diagram will be skipped.")


ROOT = os.path.dirname(os.path.dirname(__file__))
DYNAMIC_JSON = os.path.join(ROOT, "analysis", "dynamic", "dynamic_security_report.json")

OUT_SANKEY_HTML = os.path.join(ROOT, "figures", "dynamic_sankey_vuln_outcome.html")
OUT_SANKEY_PNG = os.path.join(ROOT, "figures", "dynamic_sankey_vuln_outcome.png")


def parse_filename(filename: str):
    """
    Expected format:
    code samples/{python|java}/{naive|security-aware}/{claude|gpt|gemini}/promptX.{py|java}
    """
    m = re.match(
        r"code samples/(python|java)/(naive|security-aware)/([^/]+)/prompt(\d+)\.(py|java)",
        filename
    )
    if not m:
        return None
    language, awareness, llm, prompt, _ext = m.groups()
    return {
        "language": language,
        "awareness": awareness,
        "llm": llm,
        "prompt": int(prompt),
    }


def classify_outcome(msg: str):
    """
    - Ignore timeouts
    - Keep only messages containing 'Potential' or 'Unhandled error'
    - Return outcome label or None to skip.
    """
    if "Timeout with payload" in msg:
        return None
    if "Potential" in msg:
        return "Potential"
    if "Unhandled error" in msg:
        return "Unhandled error"
    return None


def map_vuln_group(vuln_key: str) -> str:
    """
    Map detailed keys (sql_injection_cli, nosql_injection_function, etc.)
    into broader vulnerability groups.
    """
    k = vuln_key.lower()
    if k.startswith("sql_"):
        return "SQL Injection"
    if k.startswith("nosql_"):
        return "NoSQL Injection"
    if k.startswith("command_injection"):
        return "Command Injection"
    if k.startswith("path_traversal"):
        return "Path Traversal"
    if k.startswith("xss_"):
        return "XSS"
    if k.startswith("ldap_"):
        return "LDAP Injection"
    if k.startswith("xml_"):
        return "XML/XXE Injection"
    # Fallback: use raw key
    return vuln_key


# --- Load and flatten JSON ---

with open(DYNAMIC_JSON, "r") as f:
    dynamic_data = json.load(f)

results = dynamic_data.get("results", {})

rows = []

for filename, finding_dict in results.items():
    meta = parse_filename(filename)
    if meta is None:
        # Skip anything that doesn't match our pattern
        continue

    for vuln_key, messages in finding_dict.items():
        vuln_group = map_vuln_group(vuln_key)

        for msg in messages:
            outcome = classify_outcome(msg)
            if outcome is None:
                continue  # skip timeouts + anything that isn't Potential/Unhandled

            rows.append(
                {
                    "file": filename,
                    "language": meta["language"],
                    "awareness": meta["awareness"],
                    "llm": meta["llm"],
                    "prompt": meta["prompt"],
                    "vuln_key": vuln_key,
                    "vuln_group": vuln_group,
                    "outcome": outcome,
                    "count": 1,  # each message = one dynamic finding
                }
            )

df = pd.DataFrame(rows)

if df.empty:
    raise SystemExit("No non-timeout Potential/Unhandled findings found in dynamic report.")


# ============================================================================
# 2) SANKEY: Vulnerability Group → Outcome (Potential vs Unhandled)
# ============================================================================

if HAVE_PLOTLY:
    sankey_data = (
        df.groupby(["vuln_group", "outcome"])["count"]
          .sum()
          .reset_index()
    )

    totals_vg = sankey_data.groupby("vuln_group")["count"].sum()
    totals_out = sankey_data.groupby("outcome")["count"].sum()

    vuln_groups = list(sankey_data["vuln_group"].unique())
    outcomes = list(sankey_data["outcome"].unique())

    # Build node list: all vuln_groups first, then outcomes, with totals in the labels
    nodes = [f"{vg} ({int(totals_vg[vg])})" for vg in vuln_groups] + [
        f"{out} ({int(totals_out[out])})" for out in outcomes
    ]

    node_indices = {name: idx for idx, name in enumerate(nodes)}

    sources = []
    targets = []
    values = []

    for _, row in sankey_data.iterrows():
        vg = row["vuln_group"]
        out = row["outcome"]
        cnt = int(row["count"])

        sources.append(node_indices[f"{vg} ({int(totals_vg[vg])})"])
        targets.append(node_indices[f"{out} ({int(totals_out[out])})"])
        values.append(cnt)

    fig_sankey = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=nodes,
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                ),
            )
        ]
    )

    fig_sankey.update_layout(
        title_text="Dynamic (Non-timeout) Vulnerabilities: Vulnerability Group → Outcome",
        font=dict(size=12)
    )

    os.makedirs(os.path.dirname(OUT_SANKEY_HTML), exist_ok=True)
    fig_sankey.write_html(OUT_SANKEY_HTML)
    print("Saved Sankey diagram (HTML):", OUT_SANKEY_HTML)

    try:
        fig_sankey.write_image(OUT_SANKEY_PNG, scale=2)
        print("Saved Sankey diagram (PNG):", OUT_SANKEY_PNG)
    except Exception as e:
        print("Could not save Sankey PNG (install kaleido to enable static image export):", e)
else:
    print("Skipping Sankey; install plotly to enable this figure.")