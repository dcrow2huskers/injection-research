import os
import pandas as pd
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(__file__))

# --- Python Bandit CSV files ---
CSV_FILES = [
    os.path.join(ROOT, "analysis/static/python-security-aware/bandit_claude_security_aware.csv"),
    os.path.join(ROOT, "analysis/static/python-security-aware/bandit_gpt_security_aware.csv"),
    os.path.join(ROOT, "analysis/static/python-security-aware/bandit_gemini_security_aware.csv"),
    os.path.join(ROOT, "analysis/static/python-naive/bandit_claude_naive.csv"),
    os.path.join(ROOT, "analysis/static/python-naive/bandit_gpt_naive.csv"),
    os.path.join(ROOT, "analysis/static/python-naive/bandit_gemini_naive.csv"),
]

OUT_PNG = os.path.join(ROOT, "figures/bandit_figure.png")

# Injection-related test names and CWE IDs
INJECTION_RELATED = {
    # SQL Injection
    'hardcoded_sql_expressions': 'SQL Injection',
    'B608': 'SQL Injection',
    '89': 'SQL Injection',
    
    # Command Injection
    'subprocess_without_shell_equals_true': 'Command Injection',
    'subprocess_popen_with_shell_equals_true': 'Command Injection',
    'start_process_with_partial_path': 'Command Injection',
    'B602': 'Command Injection',
    'B603': 'Command Injection',
    'B605': 'Command Injection',
    '78': 'Command Injection',
    
    # Path Traversal
    'B108': 'Path Traversal',
    '377': 'Path Traversal',
}

# Store results
injection_count = 0
total_count = 0

print("Analyzing Python Bandit reports for injection vulnerabilities:\n")

all_data = []

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
    if "test_name" not in df.columns:
        print(f"WARNING: 'test_name' column not found in {path}")
        continue
    
    all_data.append(df)
    
    # Count injection-related vulnerabilities
    # Check test_name, test_id (like B608), and CWE number
    mask = (
        df["test_name"].isin(INJECTION_RELATED.keys()) |
        df["test_id"].isin(INJECTION_RELATED.keys()) |
        df["issue_cwe"].str.extract(r'/(\d+)\.html')[0].isin(INJECTION_RELATED.keys())
    )
    
    injection_in_file = mask.sum()
    total_in_file = len(df)
    
    injection_count += injection_in_file
    total_count += total_in_file
    
    filename = os.path.basename(path)
    print(f"{filename}:")
    print(f"  Injection-related: {injection_in_file}")
    print(f"  Total vulnerabilities: {total_in_file}")
    
    # Debug: show which injection types found
    if injection_in_file > 0:
        injection_types = df[mask]["test_name"].unique()
        print(f"  Injection types found: {list(injection_types)}")
    print()

non_injection_count = total_count - injection_count

print(f"{'='*60}")
print(f"Total injection-related vulnerabilities: {injection_count}")
print(f"Total other vulnerabilities: {non_injection_count}")
print(f"Total all vulnerabilities: {total_count}")
if total_count > 0:
    print(f"Injection percentage: {(injection_count/total_count*100):.1f}%")
print(f"{'='*60}")

# Check if we have data to plot
if total_count == 0:
    print("\nNo data to plot!")
    exit(1)

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)

# Create pie chart
fig, ax = plt.subplots(figsize=(10, 8))

colors = ['#dc3545', '#6c757d']
explode = (0.05, 0) if injection_count > 0 else (0, 0)

wedges, texts, autotexts = ax.pie(
    [injection_count, non_injection_count],
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
    'Injection-Related Vulnerabilities in Python Bandit Reports\n(Security-Aware & Naive Combined)',
    fontsize=14,
    fontweight='bold',
    pad=20
)

# Add count annotations
plt.text(0, -1.3, f'Injection-Related: {injection_count} | Other: {non_injection_count} | Total: {total_count}',
         ha='center', fontsize=11, style='italic')

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=300, bbox_inches='tight')
print(f"\nSaved figure: {OUT_PNG}")

# Optional: Uncomment to display the plot
# plt.show()