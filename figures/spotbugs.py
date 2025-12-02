import os
import pandas as pd
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(__file__))

# --- All six files ---
CSV_FILES = [
    os.path.join(ROOT, "analysis/static/java-security-aware/spotbugs_claude_security_aware.csv"),
    os.path.join(ROOT, "analysis/static/java-security-aware/spotbugs_gpt_security_aware.csv"),
    os.path.join(ROOT, "analysis/static/java-security-aware/spotbugs_gemini_security_aware.csv"),
    os.path.join(ROOT, "analysis/static/java-naive/spotbugs_claude_naive.csv"),
    os.path.join(ROOT, "analysis/static/java-naive/spotbugs_gpt_naive.csv"),
    os.path.join(ROOT, "analysis/static/java-naive/spotbugs_gemini_naive.csv"),
]

OUT_PNG = os.path.join(ROOT, "figures/spotbugs_figure.png")

# Store results
sql_count = 0
total_count = 0

print("Analyzing all files:\n")

for path in CSV_FILES:
    if not os.path.exists(path):
        print(f"WARNING: File not found → {path}")
        continue
    
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"ERROR: Could not read {path}: {e}")
        continue
    
    # Check if required columns exist
    if "type" not in df.columns:
        print(f"WARNING: 'type' column not found in {path}")
        continue
    
    # Count SQL-related vulnerabilities
    sql_in_file = df["type"].str.contains("SQL", case=False, na=False).sum()
    total_in_file = len(df)
    
    sql_count += sql_in_file
    total_count += total_in_file
    
    filename = os.path.basename(path)
    print(f"{filename}:")
    print(f"  Injection-Related: {sql_in_file}")
    print(f"  Total vulnerabilities: {total_in_file}")
    
    # Debug: show which types contain SQL
    sql_types = df[df["type"].str.contains("SQL", case=False, na=False)]["type"].unique()
    if len(sql_types) > 0:
        print(f"  SQL types found: {list(sql_types)}")
    print()

non_sql_count = total_count - sql_count

print(f"{'='*60}")
print(f"Total Injection-Related vulnerabilities: {sql_count}")
print(f"Total other vulnerabilities: {non_sql_count}")
print(f"Total all vulnerabilities: {total_count}")
print(f"Injection percentage: {(sql_count/total_count*100):.1f}%")
print(f"{'='*60}")

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)

# Create pie chart
fig, ax = plt.subplots(figsize=(10, 8))

colors = ['#dc3545', '#6c757d']
explode = (0.05, 0)  # slightly separate the SQL slice

wedges, texts, autotexts = ax.pie(
    [sql_count, non_sql_count],
    labels=['Injection-Related Vulnerabilities', 'Other Vulnerabilities'],
    colors=colors,
    autopct='%1.1f%%',
    startangle=90,
    explode=explode,
    textprops={'fontsize': 12}
)

# Make percentage text bold and white
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(14)

ax.set_title(
    'Injection-Related Vulnerabilities in Java SpotBugs Reports\n(Security-Aware & Naive Combined)',
    fontsize=14,
    fontweight='bold',
    pad=20
)

# Add count annotations
plt.text(0, -1.3, f'Injection-Related: {sql_count} | Other: {non_sql_count} | Total: {total_count}',
         ha='center', fontsize=11, style='italic')

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=300, bbox_inches='tight')
print(f"\nSaved figure: {OUT_PNG}")

# Optional: Uncomment to display the plot
# plt.show()