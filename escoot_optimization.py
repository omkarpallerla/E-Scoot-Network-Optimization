# =============================================================
# E-Scoot Charging Network Optimization — MILP + Gurobi
# Author: Omkar Pallerla | MS Business Analytics, ASU
# ASU Campus Facility Location Problem
# Note: Uses PuLP as open-source MILP solver (same logic as Gurobi)
# =============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')

# Try gurobipy first, fall back to PuLP
try:
    import gurobipy as gp
    from gurobipy import GRB
    SOLVER = 'gurobi'
except ImportError:
    import pulp
    SOLVER = 'pulp'

plt.style.use('dark_background')
np.random.seed(42)

# ══════════════════════════════════════════════════════════════
# CANDIDATE LOCATIONS — ASU TEMPE CAMPUS
# ══════════════════════════════════════════════════════════════
locations = pd.DataFrame({
    'name':           ['Sun Devil Fitness','Hassayampa Dorms','Tooker House',
                       'Manzanita Hall','Light Rail Stop','Greek Row',
                       'Research Park','Perimeter Rd'],
    'lat':            [33.4225, 33.4185, 33.4240, 33.4170, 33.4260, 33.4155, 33.4280, 33.4140],
    'lon':            [-111.935, -111.930, -111.928, -111.940, -111.945, -111.932, -111.920, -111.950],
    'fixed_cost':     [8500, 7200, 9100, 6800, 10200, 7500, 8800, 6200],  # $
    'charger_cost':   [450, 420, 480, 410, 520, 430, 465, 400],           # $ per charger
    'demand':         [85, 92, 78, 88, 95, 72, 68, 55],                   # daily trips
    'residential':    [0, 1, 1, 1, 0, 1, 0, 0],                          # residential coverage
    'traffic_score':  [9.2, 8.8, 7.5, 8.0, 9.5, 6.8, 6.5, 4.5]
})

print("Candidate Locations:")
print(locations[['name','fixed_cost','charger_cost','demand','residential']].to_string(index=False))

BUDGET          = 35_000
MIN_RESIDENTIAL = 0.70
TOTAL_DEMAND    = locations['demand'].sum()
N               = len(locations)

# ══════════════════════════════════════════════════════════════
# MILP FORMULATION — PuLP (same math as Gurobi)
# ══════════════════════════════════════════════════════════════
print(f"\nSolver: {SOLVER.upper()}")
print("Formulating MILP...")

prob = pulp.LpProblem("EScoot_Facility_Location", pulp.LpMinimize)

# Decision variables
y = [pulp.LpVariable(f"y_{i}", cat='Binary')       for i in range(N)]   # build station?
x = [pulp.LpVariable(f"x_{i}", lowBound=0, cat='Integer') for i in range(N)]  # chargers

# Objective: minimize total cost
total_cost = pulp.lpSum(
    locations.loc[i,'fixed_cost']  * y[i] +
    locations.loc[i,'charger_cost'] * x[i]
    for i in range(N)
)
prob += total_cost

# Constraints
# 1. Budget
prob += pulp.lpSum(
    locations.loc[i,'fixed_cost'] * y[i] +
    locations.loc[i,'charger_cost'] * x[i]
    for i in range(N)
) <= BUDGET

# 2. Demand satisfaction — total charger capacity ≥ total demand
prob += pulp.lpSum(x[i] for i in range(N)) >= TOTAL_DEMAND / 10  # 1 charger serves ~10 trips/day

# 3. Residential equity
residential_ids = locations[locations['residential'] == 1].index.tolist()
total_residential = len(residential_ids)
prob += pulp.lpSum(y[i] for i in residential_ids) >= int(MIN_RESIDENTIAL * total_residential)

# 4. Chargers only where station exists (big-M = 50)
for i in range(N):
    prob += x[i] <= 50 * y[i]

# 5. Minimum chargers per station if built
for i in range(N):
    prob += x[i] >= y[i]  # at least 1 charger if station built

# Solve
status = prob.solve(pulp.PULP_CBC_CMD(msg=0))
print(f"Status: {pulp.LpStatus[status]}")

# Extract solution
y_sol = [int(round(pulp.value(y[i]))) for i in range(N)]
x_sol = [int(round(pulp.value(x[i]))) for i in range(N)]
total_cost_sol = pulp.value(prob.objective)

locations['build_station'] = y_sol
locations['num_chargers']  = x_sol
locations['actual_cost']   = (locations['fixed_cost'] * locations['build_station'] +
                               locations['charger_cost'] * locations['num_chargers'])

selected = locations[locations['build_station'] == 1]
print(f"\n{'='*50}")
print(f"OPTIMAL SOLUTION:")
print(f"  Stations built:  {len(selected)} of {N}")
print(f"  Total cost:      ${total_cost_sol:,.0f} (Budget: ${BUDGET:,})")
print(f"  Budget saved:    ${BUDGET - total_cost_sol:,.0f} ({(BUDGET-total_cost_sol)/BUDGET*100:.1f}%)")
print(f"  Chargers total:  {sum(x_sol)}")
res_coverage = selected['residential'].mean()
print(f"  Residential cov: {res_coverage:.0%}")
print(f"\nSelected Stations:")
print(selected[['name','num_chargers','actual_cost','demand','residential']].to_string(index=False))

locations.to_csv('outputs/station_results.csv', index=False)
print("\nExported: outputs/station_results.csv")

# ══════════════════════════════════════════════════════════════
# VISUALIZATIONS
# ══════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.patch.set_facecolor('#0d1117')
COLORS = ['#4f9cf9','#06d6a0','#7c3aed','#f59e0b','#ef4444']

# Campus map
ax = axes[0, 0]
ax.set_facecolor('#0d1117')
for _, row in locations.iterrows():
    if row['build_station']:
        ax.scatter(row['lon'], row['lat'], s=200, color='#06d6a0', zorder=5,
                   marker='*', edgecolors='white', linewidths=0.5)
        ax.annotate(f"{row['name'].split()[0]}\n({row['num_chargers']} chgrs)",
                    (row['lon'], row['lat']), textcoords='offset points',
                    xytext=(6, 4), fontsize=7, color='#06d6a0')
    else:
        ax.scatter(row['lon'], row['lat'], s=60, color='#4a5568', zorder=4, marker='o')
        ax.annotate(row['name'].split()[0], (row['lon'], row['lat']),
                    textcoords='offset points', xytext=(4,3), fontsize=6, color='#4a5568')
ax.set_xlabel('Longitude'); ax.set_ylabel('Latitude')
ax.set_title('ASU Campus — Optimal Station Locations', color='white', pad=12)
green_p = mpatches.Patch(color='#06d6a0', label='Selected (★)')
gray_p  = mpatches.Patch(color='#4a5568', label='Rejected')
ax.legend(handles=[green_p, gray_p], fontsize=8)

# Cost comparison
ax = axes[0, 1]
colors_bars = ['#06d6a0' if b else '#4a5568' for b in y_sol]
ax.bar(range(N), locations['actual_cost'], color=colors_bars, alpha=0.9)
ax.set_xticks(range(N))
ax.set_xticklabels([n.split()[0] for n in locations['name']], rotation=30, ha='right', fontsize=8)
ax.axhline(BUDGET, color='#ef4444', linestyle='--', alpha=0.6, label=f'Budget ${BUDGET:,}')
ax.set_ylabel('Cost ($)')
ax.set_title('Station Cost vs Budget', color='white', pad=12)
ax.legend()

# Demand vs chargers
ax = axes[1, 0]
sel = locations[locations['build_station'] == 1]
rej = locations[locations['build_station'] == 0]
ax.scatter(sel['demand'], sel['num_chargers'], s=120, color='#06d6a0',
           label='Selected', zorder=5)
ax.scatter(rej['demand'], [0]*len(rej), s=60, color='#4a5568',
           label='Rejected', zorder=4, alpha=0.7)
for _, row in sel.iterrows():
    ax.annotate(row['name'].split()[0], (row['demand'], row['num_chargers']),
                textcoords='offset points', xytext=(4,3), fontsize=8, color='white')
ax.set_xlabel('Daily Demand (trips)'); ax.set_ylabel('Chargers Installed')
ax.set_title('Demand vs Chargers', color='white', pad=12)
ax.legend()

# Budget breakdown
ax = axes[1, 1]
budget_data = {
    'Fixed\nConstruction': sum(locations['fixed_cost'] * locations['build_station']),
    'Charger\nUnits':      sum(locations['charger_cost'] * locations['num_chargers']),
    'Budget\nRemaining':   BUDGET - total_cost_sol
}
bars = ax.bar(budget_data.keys(), budget_data.values(),
              color=['#4f9cf9','#7c3aed','#06d6a0'])
for bar, val in zip(bars, budget_data.values()):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+100,
            f'${val:,.0f}', ha='center', va='bottom', color='white', fontsize=9)
ax.set_ylabel('Amount ($)')
ax.set_title('Budget Allocation Breakdown', color='white', pad=12)

plt.tight_layout()
plt.savefig('outputs/escoot_optimization.png', dpi=150, bbox_inches='tight', facecolor='#0d1117')
print("Saved: outputs/escoot_optimization.png")
plt.show()
