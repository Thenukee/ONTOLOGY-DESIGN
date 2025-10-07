#!/usr/bin/env python3
"""
Generate simple KPI charts from output/run_logs/metrics.csv.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt

CSV = os.path.join("output", "run_logs", "metrics.csv")
FIG_DIR = os.path.join("output", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

df = pd.read_csv(CSV, index_col="step")

# Revenue over time
plt.figure()
df["revenue"].plot()
plt.title("Revenue over time")
plt.xlabel("Step")
plt.ylabel("Revenue")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "revenue.png"))
plt.close()

# Average inventory over time
plt.figure()
df["avg_inventory"].plot()
plt.title("Average Inventory over time")
plt.xlabel("Step")
plt.ylabel("Avg Inventory")
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "avg_inventory.png"))
plt.close()

print("Saved figures to", FIG_DIR)
