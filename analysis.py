"""
Healthcare Revenue & Operations Analytics -- Python analysis layer.
Reads from the SQLite DB, reproduces the SQL findings in pandas,
and produces chart images for the dashboard / portfolio write-up.
"""
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

conn = sqlite3.connect("/home/claude/healthcare_project/data/healthcare.db")
df = pd.read_sql_query("SELECT * FROM encounters", conn)

OUT = "/home/claude/healthcare_project/dashboard/assets"
import os
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#1a1a1a",
    "text.color": "#1a1a1a",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
})

NAVY = "#1F3864"
TEAL = "#2E8B8B"
CORAL = "#D9724F"
GREY = "#9AA5B1"

# ---- 1. Denial rate by payer ----
payer_stats = df.groupby("payer").agg(
    total=("encounter_id", "count"),
    denied=("claim_status", lambda x: (x == "Denied").sum())
)
payer_stats["denial_rate"] = 100 * payer_stats["denied"] / payer_stats["total"]
payer_stats = payer_stats.sort_values("denial_rate", ascending=False)

fig, ax = plt.subplots(figsize=(7, 4.2))
bars = ax.barh(payer_stats.index, payer_stats["denial_rate"], color=NAVY)
ax.set_xlabel("Denial Rate (%)")
ax.set_title("Denial Rate by Payer", fontsize=13, weight="bold", color=NAVY)
ax.invert_yaxis()
for bar, val in zip(bars, payer_stats["denial_rate"]):
    ax.text(val + 0.15, bar.get_y() + bar.get_height()/2, f"{val:.1f}%", va="center", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUT}/denial_by_payer.png", dpi=150)
plt.close()

# ---- 2. Top denial reasons by revenue at risk ----
denied = df[df["claim_status"] == "Denied"]
reason_stats = denied.groupby("denial_reason")["billed_amount"].sum().sort_values(ascending=True) / 1e7

fig, ax = plt.subplots(figsize=(7, 4.2))
bars = ax.barh(reason_stats.index, reason_stats.values, color=CORAL)
ax.set_xlabel("Revenue at Risk (Rs. Cr)")
ax.set_title("Top Denial Reasons by Revenue Impact", fontsize=13, weight="bold", color=NAVY)
for bar, val in zip(bars, reason_stats.values):
    ax.text(val + 0.002, bar.get_y() + bar.get_height()/2, f"{val:.2f} Cr", va="center", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUT}/denial_reasons.png", dpi=150)
plt.close()

# ---- 3. Monthly leakage trend ----
df["month"] = pd.to_datetime(df["service_date"]).dt.to_period("M").astype(str)
monthly = df.groupby("month").agg(
    billed=("billed_amount", "sum"),
    paid=("paid_amount", lambda x: x.fillna(0).sum())
)
monthly["leakage_pct"] = 100 * (monthly["billed"] - monthly["paid"]) / monthly["billed"]

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(monthly.index, monthly["leakage_pct"], color=NAVY, marker="o", markersize=4, linewidth=2)
ax.fill_between(monthly.index, monthly["leakage_pct"], color=NAVY, alpha=0.08)
ax.set_title("Monthly Revenue Leakage Trend", fontsize=13, weight="bold", color=NAVY)
ax.set_ylabel("Leakage (%)")
ax.set_xticks(range(0, len(monthly.index), 3))
ax.set_xticklabels(monthly.index[::3], rotation=45, ha="right")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUT}/leakage_trend.png", dpi=150)
plt.close()

# ---- 4. Department collection rate ----
dept = df.groupby("department").agg(
    billed=("billed_amount", "sum"),
    paid=("paid_amount", lambda x: x.fillna(0).sum())
)
dept["collection_rate"] = 100 * dept["paid"] / dept["billed"]
dept = dept.sort_values("collection_rate")

fig, ax = plt.subplots(figsize=(7, 4.2))
bars = ax.barh(dept.index, dept["collection_rate"], color=TEAL)
ax.set_xlabel("Collection Rate (%)")
ax.set_title("Collection Rate by Department", fontsize=13, weight="bold", color=NAVY)
ax.set_xlim(60, 78)
for bar, val in zip(bars, dept["collection_rate"]):
    ax.text(val + 0.1, bar.get_y() + bar.get_height()/2, f"{val:.1f}%", va="center", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUT}/collection_by_dept.png", dpi=150)
plt.close()

# ---- Summary stats for README / dashboard KPIs ----
total_billed = df["billed_amount"].sum() / 1e7
total_paid = df["paid_amount"].fillna(0).sum() / 1e7
leakage_pct = 100 * (total_billed - total_paid) / total_billed
denial_rate = 100 * (df["claim_status"] == "Denied").mean()
encounters = len(df)

summary = f"""
KEY METRICS
-----------
Total Encounters:        {encounters:,}
Total Billed Revenue:    Rs. {total_billed:.2f} Cr
Total Collected Revenue: Rs. {total_paid:.2f} Cr
Revenue Leakage:         {leakage_pct:.1f}%
Overall Denial Rate:     {denial_rate:.1f}%
Top Denial Driver:       {reason_stats.idxmax()} (Rs. {reason_stats.max():.2f} Cr at risk)
Highest-Denial Payer:    {payer_stats['denial_rate'].idxmax()} ({payer_stats['denial_rate'].max():.1f}%)
"""
print(summary)
with open("/home/claude/healthcare_project/dashboard/assets/summary_stats.txt", "w") as f:
    f.write(summary)

import json
kpi = {
    "encounters": int(encounters),
    "total_billed_cr": round(total_billed, 2),
    "total_collected_cr": round(total_paid, 2),
    "leakage_pct": round(leakage_pct, 1),
    "denial_rate": round(denial_rate, 1),
    "payer_denial": payer_stats["denial_rate"].round(1).to_dict(),
    "reason_risk_cr": reason_stats.round(2).to_dict(),
    "monthly_leakage": monthly["leakage_pct"].round(1).to_dict(),
    "dept_collection": dept["collection_rate"].round(1).to_dict(),
}
with open("/home/claude/healthcare_project/dashboard/assets/kpi_data.json", "w") as f:
    json.dump(kpi, f, indent=2)

print("Charts + KPI data written.")
