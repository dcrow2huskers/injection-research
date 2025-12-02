# figures/injection_llm_lang_awareness.py

import os
import json
import re
import pandas as pd
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(__file__))

JAVA_JSON = os.path.join(ROOT, "analysis", "static", "java_security_report.json")
PY_JSON   = os.path.join(ROOT, "analysis", "static", "python_security_report.json")
OUT_PNG   = os.path.join(ROOT, "figures", "custom_static_analysis.png")


def load_security_report(path):
    with open(path, "r") as f:
        data = json.load(f)

    rows = []
    for filename, findings in data.items():
        m = re.match(
            r"code samples/(java|python)/(naive|security-aware)/(.+?)/prompt(\d+)\.(java|py)",
            filename,
            re.IGNORECASE,
        )
        if not m:
            continue
        language, awareness, llm, prompt, _ext = m.groups()
        language = language.title()
        awareness = awareness.title().replace("-aware", "-Aware")

        for vuln_type, messages in findings.items():
            rows.append(
                {
                    "file": filename,
                    "language": language,
                    "awareness": awareness, 
                    "llm": llm,             
                    "prompt": int(prompt),
                    "vuln_type": vuln_type,
                    "count": len(messages),
                }
            )

    return pd.DataFrame(rows)


def is_injection(vuln_type: str) -> bool:
    vt = vuln_type.lower()
    # True injection categories
    if "injection" in vt:
        return True
    if "sql" in vt:
        return True
    if "mongodb" in vt:
        return True
    # Python dangerous primitives (eval/exec/compile/input without validation)
    if vt == "dangerous_functions":
        return True
    return False


dfs = []
for path in [JAVA_JSON, PY_JSON]:
    if os.path.exists(path):
        dfs.append(load_security_report(path))
    else:
        print(f"WARNING: missing report: {path}")

if not dfs:
    raise SystemExit("No security reports found")

df = pd.concat(dfs, ignore_index=True)

if df.empty:
    raise SystemExit("No rows parsed from security reports; check filename patterns in load_security_report().")

# Keep only injection-related vulns, ignore things like hardcoded_secrets
df_inj = df[df["vuln_type"].apply(is_injection)].copy()

if df_inj.empty:
    raise SystemExit("No injection-related findings after filtering")

# Aggregate: total injection findings per (language, llm, awareness)
agg = (
    df_inj
    .groupby(["language", "llm", "awareness"])["count"]
    .sum()
    .reset_index()
)

# Pivot for stacked bar: index = "language-llm", columns = awareness
agg["lang_llm"] = agg["llm"].str.capitalize() + ", " + agg["language"]
pivot = agg.pivot_table(
    index="lang_llm",
    columns="awareness",
    values="count",
    aggfunc="sum",
    fill_value=0,
)

# Optional column order
col_order = [c for c in ["Naive", "Security-Aware"] if c in pivot.columns]
pivot = pivot[col_order]

ax = pivot.plot(
    kind="bar",
    stacked=True,
    figsize=(10, 5),
    color=["#6A5ACD", "#D2B48C"]
)
ax.set_title("Injection Findings by Language, LLM, and Prompt Style (Line-by-Line Counts)")
ax.set_xlabel("Language & LLM")
ax.set_ylabel("Total Injection Findings")
ax.legend(title="Prompt Style")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
plt.savefig(OUT_PNG, dpi=300)
# plt.show()

print("Saved figure:", OUT_PNG)
print("\nAggregated injection counts (line-by-line):\n", pivot)