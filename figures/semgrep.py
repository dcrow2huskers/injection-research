import os
import pandas as pd
import matplotlib.pyplot as plt


ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  # repo root
CSV_PATH = os.path.join(ROOT_DIR, "analysis", "static", "semgrep_static_analysis.csv")
OUT_PATH = os.path.join(ROOT_DIR, "figures", "semgrep_figure.png")


df = pd.read_csv(CSV_PATH)

def detect_llm(url):
    if not isinstance(url, str):
        return "Unknown"
    u = url.lower()
    if "claude" in u:
        return "Claude"
    if "gemini" in u:
        return "Gemini"
    if "gpt" in u:
        return "GPT"


df["LLM"] = df["Line Of Code Url"].apply(detect_llm)


grouped = (
    df.groupby(["LLM", "Severity"])
      .size()
      .unstack(fill_value=0)
)


ax = grouped.plot(kind="bar", figsize=(7, 4))
ax.set_xlabel("LLM")
ax.set_ylabel("Count")
ax.set_title("Semgrep Findings by LLM and Severity")
plt.tight_layout()

plt.savefig(OUT_PATH, dpi=300)
plt.show()